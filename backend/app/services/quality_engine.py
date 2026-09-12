"""Quality engine — deterministic compliance scoring against content standards."""

import re

from app.services.rules_engine import (
    CHAR_LIMITS,
    PLACEHOLDERS,
    UOM_APPROVED,
    is_placeholder,
)

APPROVED_UOMS = set(UOM_APPROVED.keys()) | {k.upper() for k in UOM_APPROVED.keys()} | {"K", "k"}

CHECK_TO_FIELD_MAP = {
    "TITLE": "product_name",
    "TITLE_LEN": "product_name",
    "INVOICE": "invoice_desc",
    "INV_LIMIT": "invoice_desc",
    "INV_CAPS": "invoice_desc",
    "MOBILE_RANGE": "mobile_desc",
    "LONG": "long_desc",
    "ATTR_COUNT": "attributes",
    "UOM": "attributes",
    "CLASSPATH": "classpath",
    "NO_PLACEHOLDER": "product_name",
}


def check_quality(item_fields: dict) -> dict:
    """Run all compliance checks. Returns {score, checks: [{id,label,passed,detail}]}."""
    checks: list[dict] = []

    def add(cid: str, label: str, passed: bool, detail: str = "") -> None:
        checks.append({"id": cid, "label": label, "passed": bool(passed), "detail": detail})

    title = item_fields.get("product_name") or ""
    add("TITLE", "Product title present", bool(title.strip()), f"{len(title)} chars")
    add("TITLE_LEN", "Title <= 120 chars", 0 < len(title) <= 120)

    inv = item_fields.get("invoice_desc") or ""
    limit = CHAR_LIMITS["invoice_desc"]
    add("INVOICE", "Invoice desc present", bool(inv.strip()))
    add("INV_LIMIT", f"Invoice desc <= {limit} chars", len(inv) <= limit, f"{len(inv)} chars")
    add("INV_CAPS", "Invoice desc ALL CAPS", inv.isupper() if inv else False)

    mob = item_fields.get("mobile_desc") or ""
    lo, hi = CHAR_LIMITS["mobile_desc_min"], CHAR_LIMITS["mobile_desc_max"]
    add("MOBILE_RANGE", f"Mobile desc {lo}-{hi} chars", lo - 10 <= len(mob) <= hi + 10, f"{len(mob)} chars")

    add("LONG", "Long description present", bool((item_fields.get("long_desc") or "").strip()))

    attrs = item_fields.get("attributes") or []
    add("ATTR_COUNT", "At least 3 attributes", isinstance(attrs, list) and len(attrs) >= 3, f"{len(attrs)}")

    bad_uom = []
    canon_uoms_lower = {u.lower() for u in APPROVED_UOMS}
    for a in attrs:
        uom = (a.get("uom") or "").strip()
        if uom and uom not in APPROVED_UOMS and uom.lower() not in canon_uoms_lower:
            bad_uom.append(uom)
    add("UOM", "All units use approved abbreviations", not bad_uom, ", ".join(sorted(set(bad_uom))[:4]))

    cp = item_fields.get("classpath") or ""
    depth = len([p for p in re.split(r"\s*>\s*", cp) if p])
    add("CLASSPATH", "Classpath has 3 levels", depth == 3, f"{depth} levels")

    text_blob = " ".join(
        str(item_fields.get(k) or "") for k in (
            "product_name", "short_desc", "long_desc",
            "marketing_description", "retail_desc",
        )
    ).lower()
    has_placeholder = any(p in text_blob for p in ("-- unbranded --", "-- no unilog brand --", "-- no dib brand --", "n/a"))
    add("NO_PLACEHOLDER", "No placeholder values leaked into output", not has_placeholder)

    passed = sum(1 for c in checks if c["passed"])
    return {
        "score": round(passed / len(checks) * 100, 1),
        "checks": checks,
        "passed_count": passed,
        "failed_count": len(checks) - passed,
    }


def needs_human_review(ai_result: dict, quality: dict) -> tuple[bool, list[str]]:
    """Decide HITL escalation from AI confidence + failed checks."""
    flags = set(ai_result.get("low_confidence_fields") or [])
    conf = float(ai_result.get("confidence") or 0.0)
    review = conf < 0.65 or bool(flags)
    critical_failed = [c["id"] for c in quality["checks"] if not c["passed"] and c["id"] in {
        "TITLE", "INVOICE", "LONG", "ATTR_COUNT", "CLASSPATH"}]
    if critical_failed:
        review = True
        for cid in critical_failed:
            flags.add(CHECK_TO_FIELD_MAP.get(cid, cid))
    return review, sorted(flags)


FIELD_GROUP_MAP = {
    "dept": "taxonomy", "item_class": "taxonomy", "fine": "taxonomy",
    "classpath": "taxonomy", "unspsc": "taxonomy",
    "brand_name": "identity", "trade_name": "identity", "manufacturer_name": "identity",
    "product_name": "descriptions", "invoice_desc": "descriptions",
    "mobile_desc": "descriptions", "short_desc": "descriptions",
    "long_desc": "descriptions", "marketing_description": "descriptions",
    "attributes": "attributes", "features": "attributes",
}
