"""Gemini-powered catalog enrichment service.

One batched call enriches up to N catalog rows: classification, brand
resolution, five description variants (each following a distinct formula and
char limit), structured attributes with approved UOMs, plus per-item
confidence, reasoning, and low-confidence field flags for the HITL queue.

Includes a deterministic offline fallback so demos never break without an API key.
"""

import asyncio
import json
import os
from typing import Any, Optional

from app.services.rules_engine import (
    ABBREVIATIONS,
    enforce_invoice_desc,
    enforce_mobile_desc,
    expand_abbreviations,
    parse_manufacturer,
)

try:
    from google import genai
    from google.genai import types
except ImportError:  # pragma: no cover
    genai = None
    types = None

from app.utils.logger import get_logger

logger = get_logger(__name__)

MODEL_CASCADE = [
    "gemini-flash-lite-latest",
    "gemini-3.6-flash",
    "gemini-3.1-flash-lite",
    "gemini-flash-latest",
]

SYSTEM_PROMPT = """You are CatalogIQ Enrichment Agent for industrial/consumer product catalogs.
Given raw catalog rows (part number + cryptic abbreviated description), produce commerce-ready
product intelligence. You MUST follow these house rules exactly:

TAXONOMY:
- dept / item_class / fine: 3-level merchandise hierarchy (e.g. Tools > Power Tool Accessories > Sanding Belts).
- classpath: "Level1 > Level2 > Level3" using "&" only inside a single level name when unavoidable.
- Use standard retail/industrial taxonomy vocabulary. unspsc: best-effort 8-digit code or "".

BRAND RESOLUTION:
- Detect the actual product BRAND from the part description (e.g. "Diablo", "3M", "Festool", "Trex", "GT-Lite").
- manufacturer_name: legal manufacturer entity derived from part_manuf input; keep suffix casing like Inc, LLC, Ltd.
- trade_name: trademark line/family if identifiable, else "".
- Never invent brands not supported by the input text.

DESCRIPTION FORMULAS (all in English, no ALL CAPS except invoice_desc):
- product_name (Product Title): "<Brand> <MPN> <Item Type> <Key Differentiator(s)>" - concise, searchable, <=120 chars.
  Example: "Diablo DCB518ASTS06G 1/2 in x 18 in Sanding Belt 6-Pack".
- invoice_desc: <=40 chars, ALL CAPS, telegraphic: "SANDING BELT 1/2X18 6PK".
- mobile_desc: 60-80 chars, pattern "<Brand>, <Item Type>, <key specs>" e.g.
  "Diablo 1/2 in x 18 in Sanding Belt, Cubitron II Abrasive, 6 per Pack".
- short_desc: one sentence, <=160 chars, feature-led.
- long_desc: full sentence with dimensions using approved units (space between number and unit,
  fractions preferred: 50-1/4 in), key attributes, materials, quantities.
- marketing_description: 1-2 persuasive sentences for PDP hero copy.
- features: up to 10 short bullet phrases (no ending punctuation).

ATTRIBUTES:
- 5-12 attribute triplets with clean Label (Title Case), normalized Value, approved uom code from this set:
  in, ft, mm, cm, m, V, A, W, kW, dBA, lb, kg, oz, ga, qt, psi, rpm, hp, °F, °C, pc, pk, pr, cfm, lm, K, ""
- Expand trade abbreviations to full words (SS -> Stainless Steel, WH -> White).
- Convert decimal inches to fractions (0.25 -> 1/4). Keep number-space-unit spacing everywhere.

OUTPUT: strict JSON object {"results": [...]} one entry per input row, same order, each:
{"index": int, "item_type": str, "dept": str, "item_class": str, "fine": str, "classpath": str,
 "unspsc": str, "brand_name": str, "trade_name": str, "manufacturer_name": str,
 "product_name": str, "invoice_desc": str, "mobile_desc": str, "short_desc": str,
 "long_desc": str, "marketing_description": str, "features": [str],
 "attributes": [{"label": str, "value": str, "uom": str}],
 "confidence": float 0-1, "reasoning": str,
 "low_confidence_fields": [str]}"""


class GeminiEnrichmentService:
    def __init__(self):
        self._client = None
        # Real engine status, verified by actual call outcomes:
        # "unverified" | "live" | "fallback"
        self.last_status: str = "unverified"

    @property
    def api_key(self) -> Optional[str]:
        return (
            os.getenv("GEMINI_API_KEY")
            or os.getenv("GOOGLE_API_KEY")
            or os.getenv("GEMINI_KEY")
        )

    @property
    def is_available(self) -> bool:
        return bool(self.api_key and self.api_key.strip()) and genai is not None

    def _get_client(self):
        if self._client is None:
            self._client = genai.Client(api_key=self.api_key.strip())
        return self._client

    async def generate_json(self, prompt: str, max_tokens: int = 8192) -> dict:
        client = self._get_client()
        config = types.GenerateContentConfig(
            temperature=0.1,
            max_output_tokens=max_tokens,
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
        )
        last_error: Optional[Exception] = None
        model = os.getenv("GEMINI_MODEL") or MODEL_CASCADE[0]
        for candidate in [model] + MODEL_CASCADE:
            try:
                response = await client.aio.models.generate_content(
                    model=candidate, contents=prompt, config=config
                )
                if response and response.text:
                    return json.loads(response.text)
                last_error = RuntimeError(f"{candidate}: empty response")
            except Exception as exc:  # try next model in cascade
                logger.warning(f"Model {candidate} failed: {exc}")
                last_error = exc
        raise last_error or RuntimeError("All models failed")

    async def enrich_batch(self, rows: list[dict]) -> list[dict]:
        """rows: [{index, mfg_part_num, part_desc, e1_brand, unilog_brand, dib_brand, part_manuf}]"""
        prompt = (
            "Enrich these catalog rows now. Return strictly JSON per the schema.\n\n"
            "ROWS:\n"
            + json.dumps(
                [
                    {
                        "index": r.get("index"),
                        "mfg_part_num": r.get("mfg_part_num", ""),
                        "part_desc": r.get("part_desc", ""),
                        "e1_brand": "" if r.get("e1_brand") in ("-- Unbranded --", "-") else r.get("e1_brand", ""),
                        "dib_brand": "" if r.get("dib_brand") in ("-- No DIB Brand --", "-") else r.get("dib_brand", ""),
                        "part_manuf": r.get("part_manuf", ""),
                    }
                    for r in rows
                ],
                ensure_ascii=False,
            )
        )
        data = await self.generate_json(prompt)
        results = data.get("results", data if isinstance(data, list) else [])
        by_index = {r.get("index"): r for r in results if isinstance(r, dict)}
        out = []
        for r in rows:
            enriched = by_index.get(r.get("index"))
            out.append(enriched if isinstance(enriched, dict) else {})
        return out


# ---------------------------------------------------------------------------
# Offline deterministic fallback (no API key) — keeps the demo alive
# ---------------------------------------------------------------------------

# Known brand tokens scanned from descriptions
BRAND_LEXICON = [
    "3M", "Diablo", "Festool", "Trex", "Whirlpool", "Frigidaire", "GE",
    "Philips", "Keystone", "Makita", "DeWalt", "Bosch", "Milwaukee",
    "Klein", "Lenox", "Irwin", "Stanley", "Husqvarna", "GT-Lite", "Sylvania",
    "Eaton", "Hubbell", "Legrand", "Parker", "SKF", "Timken", "Zurn",
]

# keyword -> (dept, item_class, fine) for offline classification
CATEGORY_KEYWORDS: list[tuple[str, str, str, str]] = [
    ("sanding belt", "Tools", "Power Tool Accessories", "Sanding Belts"),
    ("abrasive", "Tools", "Power Tool Accessories", "Abrasives"),
    ("sandpaper", "Tools", "Power Tool Accessories", "Sandpaper"),
    ("drill bit", "Tools", "Power Tool Accessories", "Drill Bits"),
    ("led bulb", "Electrical", "Lighting", "LED Bulbs"),
    ("led", "Electrical", "Lighting", "LED Lighting"),
    ("bulb", "Electrical", "Lighting", "Light Bulbs"),
    ("lamp", "Electrical", "Lighting", "Lamps"),
    ("bearing", "Industrial", "Power Transmission", "Bearings"),
    ("v-belt", "Industrial", "Power Transmission", "V-Belts"),
    ("valve", "Industrial", "Plumbing", "Valves"),
    ("fitting", "Industrial", "Plumbing", "Fittings"),
    ("coupling", "Industrial", "Plumbing", "Couplings"),
    ("rail kit", "Building Materials", "Decking & Railing", "Railing Kits"),
    ("baluster", "Building Materials", "Decking & Railing", "Balusters"),
    ("railing", "Building Materials", "Decking & Railing", "Railings"),
    ("dishwasher", "Appliances", "Large Appliances", "Dishwashers"),
    ("glove", "Safety", "Personal Protection", "Gloves"),
    ("helmet", "Safety", "Personal Protection", "Head Protection"),
    ("cable", "Electrical", "Electrical Distribution", "Cables"),
    ("wire", "Electrical", "Electrical Distribution", "Wire"),
    ("switch", "Electrical", "Wiring Devices", "Switches"),
]


def _detect_brand(desc: str) -> str:
    """Scan description for a known brand token (word-boundary match)."""
    low = f" {desc.lower().replace(chr(34), ' ')} "
    for brand in BRAND_LEXICON:
        b = brand.lower()
        if f" {b} " in low or f" {b}," in low or f" {b}-" in low or f" {b}/" in low:
            return brand
    return ""


def _classify_fallback(desc: str) -> tuple[str, str, str]:
    """Keyword-based classification for fallback mode."""
    low = f" {desc.lower()} "
    for kw, dept, cls, fine in CATEGORY_KEYWORDS:
        if f" {kw}" in low or low.startswith(f" {kw}"):
            return dept, cls, fine
    return "", "", ""


def fallback_enrich_row(row: dict) -> dict:
    mpn = row.get("mfg_part_num", "")
    desc = row.get("part_desc", "") or mpn
    expanded, terms = expand_abbreviations(desc)
    manuf_raw, _code = parse_manufacturer(row.get("part_manuf", ""))
    dib = row.get("dib_brand", "")
    brand = ""
    for cand in (row.get("e1_brand"), dib):
        cand = cand or ""
        if cand and "--" not in cand:
            brand = cand
            break
    if not brand:
        brand = _detect_brand(desc)  # scan description for known brands
    tokens = [t for t in expanded.replace(mpn, "").split() if t]
    item_type = next(
        (w for w in reversed(tokens) if w.lower() not in ("pk", "pc", "set")),
        tokens[-1] if tokens else "Product",
    )
    title = f"{brand} {mpn} {' '.join(tokens[:6])}".strip()[:120]
    invoice = enforce_invoice_desc(" ".join(tokens[:6]) or mpn)
    mobile = enforce_mobile_desc(f"{brand}, {item_type}, {mpn}" if brand else f"{item_type}, {mpn}")
    attrs = [
        {"label": t.title(), "value": ABBREVIATIONS.get(t.upper(), t), "uom": ""}
        for t in terms[:6]
    ]

    # offline classification via keyword map
    dept, cls, fine_cls = _classify_fallback(expanded)
    if not dept:
        dept, fine_cls = "General", item_type
        cls = "Merchandise"
    classpath = f"{dept} > {cls} > {fine_cls}"

    return {
        "index": row.get("index"),
        "item_type": item_type,
        "dept": dept,
        "item_class": cls,
        "fine": fine_cls,
        "classpath": classpath,
        "unspsc": "",
        "brand_name": brand,
        "trade_name": "",
        "manufacturer_name": manuf_raw or brand,
        "product_name": title,
        "invoice_desc": invoice,
        "mobile_desc": mobile,
        "short_desc": expanded[:160],
        "long_desc": f"{expanded}. Part number {mpn}.",
        "marketing_description": expanded,
        "features": [],
        "attributes": attrs,
        "confidence": 0.35,
        "reasoning": "Offline rules-based fallback: abbreviation expansion + template assembly.",
        "low_confidence_fields": ["classpath", "brand_name", "attributes"],
    }


service = GeminiEnrichmentService()


async def enrich_rows(rows: list[dict]) -> list[dict]:
    """Public entrypoint — live AI when available, deterministic fallback otherwise.

    Tracks the real engine status (verified by actual call results, not just
    key presence) so the UI never claims 'Live' while running fallback.
    """
    if service.is_available:
        try:
            results = await service.enrich_batch(rows)
            service.last_status = "live"
            return results
        except Exception as exc:
            logger.error(f"Gemini enrichment failed, using fallback: {exc}")
    service.last_status = "fallback"
    await asyncio.sleep(0)
    return [fallback_enrich_row(r) for r in rows]
