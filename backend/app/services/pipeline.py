"""Batch enrichment pipeline orchestrator.

Reads pending CatalogItems for a run, calls the AI in batches with bounded
concurrency, applies deterministic post-processing (char limits, UOM rules,
provenance capture), scores quality, and creates HITL validation entries.
"""

import asyncio
import time
from typing import Any

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models.catalog import CatalogItem, PipelineRun, ValidationItem, utcnow
from app.services.enrichment_ai import enrich_rows
from app.services.quality_engine import (
    FIELD_GROUP_MAP,
    check_quality,
    needs_human_review,
)
from app.services.rules_engine import (
    enforce_invoice_desc,
    enforce_mobile_desc,
    is_placeholder,
    normalise_entity_case,
    parse_manufacturer,
)
from app.utils.logger import get_logger

logger = get_logger(__name__)

BATCH_SIZE = 8          # rows per AI call
CONCURRENCY = 3         # parallel AI calls


def _clean_brand(v: str | None) -> str:
    return "" if is_placeholder(v) else str(v or "").strip()


def postprocess_row(item: CatalogItem, ai: dict) -> dict:
    """Merge raw input + AI output into final item fields, capturing provenance."""
    prov: dict[str, Any] = {}
    conf = float(ai.get("confidence") or 0.5)
    reasoning = ai.get("reasoning") or ""

    def mark(field: str, value: Any, source: str, method: str = "") -> Any:
        if value is not None and value != "":
            prov[field] = {
                "source": source, "method": method,
                "confidence": conf if source == "ai" else 1.0 if source == "input" else 0.95,
                **({"reasoning": reasoning} if source == "ai" else {}),
            }
        return value

    # --- identity ---
    manuf_rule, manuf_code = parse_manufacturer(item.part_manuf_raw)
    manufacturer = ai.get("manufacturer_name") or normalise_entity_case(manuf_rule)
    brand = _clean_brand(ai.get("brand_name")) or _clean_brand(item.e1_brand_raw) \
        or _clean_brand(item.dib_brand_raw)
    trade = _clean_brand(ai.get("trade_name"))

    fields = {
        "manufacturer_name": mark("manufacturer_name", manufacturer, "ai" if ai.get("manufacturer_name") else "rule"),
        "brand_name": mark("brand_name", brand, "ai" if ai.get("brand_name") else "input"),
        "trade_name": mark("trade_name", trade, "ai"),
        "manufacturer_part_number": mark("manufacturer_part_number", item.mfg_part_number, "input"),
        "dept": mark("dept", ai.get("dept"), "ai"),
        "item_class": mark("item_class", ai.get("item_class"), "ai"),
        "fine": mark("fine", ai.get("fine"), "ai"),
        "classpath": mark("classpath", ai.get("classpath"), "ai"),
        "unspsc": mark("unspsc", ai.get("unspsc") or "", "ai"),
        "product_name": mark("product_name", (ai.get("product_name") or "").strip()[:200], "ai"),
        "short_desc": mark("short_desc", (ai.get("short_desc") or "").strip(), "ai"),
        "long_desc": mark("long_desc", (ai.get("long_desc") or "").strip(), "ai"),
        "retail_desc": mark("retail_desc", (ai.get("retail_desc") or "").strip(), "ai"),
        "marketing_description": mark("marketing_description", (ai.get("marketing_description") or "").strip(), "ai"),
        "applications": mark("applications", ai.get("application") or "", "ai"),
        "includes": mark("includes", ai.get("includes") or "", "ai"),
        "standards_approvals": mark("standards_approvals", ai.get("standard_approvals") or "", "ai"),
        # rule-enforced fields
        "invoice_desc": mark(
            "invoice_desc",
            enforce_invoice_desc(ai.get("invoice_desc") or ""),
            "rule", "AI draft + house char-limit/caps enforcement",
        ),
        "mobile_desc": mark(
            "mobile_desc",
            enforce_mobile_desc(ai.get("mobile_desc") or ""),
            "rule", "AI draft + 60-80 char window enforcement",
        ),
        "features": [str(f).strip() for f in (ai.get("features") or []) if str(f).strip()][:10],
        "attributes": [],
    }
    if fields["features"]:
        prov["features"] = {"source": "ai", "confidence": conf}

    attrs_out = []
    for a in (ai.get("attributes") or [])[:20]:
        if not isinstance(a, dict) or not a.get("label"):
            continue
        attr = {
            "label": str(a.get("label")).strip(),
            "value": str(a.get("value", "")).strip(),
            "uom": str(a.get("uom") or "").strip(),
        }
        if attr["value"]:
            attrs_out.append(attr)
    fields["attributes"] = attrs_out
    if attrs_out:
        prov["attributes"] = {"source": "ai", "confidence": conf, "count": len(attrs_out)}

    quality = check_quality(fields)
    review, flags = needs_human_review(ai, quality)

    return {
        "fields": fields,
        "provenance": prov,
        "quality": quality,
        "ai_confidence": round(conf, 3),
        "needs_review": review,
        "review_flags": flags,
    }


async def _process_batch(run_id: str, batch: list[CatalogItem]) -> None:
    """Enrich one batch of items and persist results."""
    item_ids = [it.id for it in batch]
    async with AsyncSessionLocal() as db:
        try:
            # Re-attach items in THIS session (batch was loaded elsewhere)
            res = await db.execute(
                select(CatalogItem).where(CatalogItem.id.in_(item_ids))
            )
            items = {row.id: row for row in res.scalars().all()}
            ordered = [items[i] for i in item_ids if i in items]

            rows = [
                {
                    "index": i,
                    "mfg_part_num": it.mfg_part_number,
                    "part_desc": it.part_desc_raw,
                    "e1_brand": it.e1_brand_raw,
                    "unilog_brand": it.unilog_brand_raw,
                    "dib_brand": it.dib_brand_raw,
                    "part_manuf": it.part_manuf_raw,
                }
                for i, it in enumerate(ordered)
            ]
            t0 = time.monotonic()
            results = await enrich_rows(rows)
            logger.info(f"Batch of {len(rows)} enriched in {time.monotonic()-t0:.1f}s")

            for item, result in zip(ordered, results):
                merged = postprocess_row(item, result)

                for key, value in merged["fields"].items():
                    setattr(item, key, value)
                item.provenance = merged["provenance"]
                item.quality_score = merged["quality"]["score"]
                item.quality_checks = {
                    "score": merged["quality"]["score"],
                    "checks": merged["quality"]["checks"],
                    "flags": merged["review_flags"],
                }
                item.ai_confidence = merged["ai_confidence"]
                item.needs_review = merged["needs_review"]
                item.status = "needs_review" if merged["needs_review"] else "enriched"
                item.error_message = None

                # HITL entries for flagged fields
                if merged["review_flags"] and result:
                    for flag in merged["review_flags"][:6]:
                        group = FIELD_GROUP_MAP.get(flag, "descriptions")
                        proposed = merged["fields"].get(flag)
                        if proposed in (None, "", []) or (
                            isinstance(proposed, list) and not any(proposed)
                        ):
                            continue
                        db.add(ValidationItem(
                            item_id=item.id,
                            run_id=run_id,
                            field_group=group,
                            field_name=flag,
                            current_value=None,
                            proposed_value=str(proposed)[:4000],
                            reason=(result.get("reasoning") or "")[:1500],
                            ai_confidence=merged["ai_confidence"],
                        ))
            await db.commit()
        except Exception as exc:
            await db.rollback()
            logger.error(f"Batch failed: {exc}")
            await db.execute(
                update(CatalogItem)
                .where(CatalogItem.id.in_(item_ids))
                .values(status="failed", error_message=str(exc)[:500])
            )
            await db.commit()
            async with AsyncSessionLocal() as db2:
                run = await db2.get(PipelineRun, run_id)
                if run:
                    run.failed_items = (run.failed_items or 0) + len(item_ids)
                    await db2.commit()


async def run_pipeline(run_id: str) -> None:
    """Main worker loop for a pipeline run."""
    async with AsyncSessionLocal() as db:
        run = await db.get(PipelineRun, run_id)
        if not run:
            return
        run.status = "running"
        run.started_at = utcnow()
        await db.commit()

    try:
        semaphore = asyncio.Semaphore(CONCURRENCY)

        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(CatalogItem)
                .where(CatalogItem.run_id == run_id, CatalogItem.status == "pending")
                .order_by(CatalogItem.row_index)
            )
            items = list(result.scalars().all())

        batches = [
            items[i : i + BATCH_SIZE] for i in range(0, len(items), BATCH_SIZE)
        ]

        async def guarded(batch: list[CatalogItem]) -> None:
            async with semaphore:
                await _process_batch(run_id, batch)

        for chunk_start in range(0, len(batches), CONCURRENCY):
            chunk = batches[chunk_start : chunk_start + CONCURRENCY]
            await asyncio.gather(*(guarded(b) for b in chunk))
            async with AsyncSessionLocal() as db:
                done = await db.execute(
                    select(func.count())
                    .select_from(CatalogItem)
                    .where(
                        CatalogItem.run_id == run_id,
                        CatalogItem.status != "pending",
                    )
                )
                await db.execute(
                    update(PipelineRun)
                    .where(PipelineRun.id == run_id)
                    .values(processed_items=done.scalar_one())
                )
                await db.commit()

        async with AsyncSessionLocal() as db:
            res = await db.execute(
                select(
                    CatalogItem.status,
                    CatalogItem.needs_review,
                ).where(CatalogItem.run_id == run_id)
            )
            all_rows = res.all()
            stats = {
                "enriched": sum(1 for s, _ in all_rows if s == "enriched"),
                "needs_review": sum(1 for _, nr in all_rows if nr),
                "failed": sum(1 for s, _ in all_rows if s == "failed"),
            }
            await db.execute(
                update(PipelineRun)
                .where(PipelineRun.id == run_id)
                .values(
                    status="completed",
                    completed_at=utcnow(),
                    processed_items=len(all_rows),
                    stats=stats,
                )
            )
            await db.commit()
        logger.info(f"Run {run_id} completed: {stats}")

    except Exception as exc:
        logger.error(f"Run {run_id} failed: {exc}")
        async with AsyncSessionLocal() as db:
            await db.execute(
                update(PipelineRun)
                .where(PipelineRun.id == run_id)
                .values(status="failed", error_message=str(exc)[:500], completed_at=utcnow())
            )
            await db.commit()
