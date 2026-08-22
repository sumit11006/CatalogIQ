"""Runs & catalog items API — upload, orchestrate, inspect."""

import csv
import io
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, Query, UploadFile
from sqlalchemy import desc, func, or_, select

from app.database import get_db
from app.models.catalog import CatalogItem, PipelineRun
from app.services.pipeline import run_pipeline
from app.services.rules_engine import is_placeholder
from app.utils.logger import get_logger

router = APIRouter(prefix="/runs", tags=["runs"])
logger = get_logger(__name__)

_ASSETS = Path(__file__).resolve().parent.parent / "assets"
SAMPLE_CSV = _ASSETS / "sample_input.csv"


def _parse_csv_rows(text: str) -> list[dict]:
    reader = csv.DictReader(io.StringIO(text))
    rows = []
    for i, r in enumerate(reader):
        rows.append({
            "row_index": i,
            "mfg_part_num": (r.get("Mfg_Part_Num") or "").strip(),
            "part_desc": (r.get("Part_Desc") or "").strip(),
            "e1_brand": (r.get("E1_Brand") or "").strip(),
            "unilog_brand": (r.get("Unilog_Brand") or "").strip(),
            "dib_brand": (r.get("DIB_Brand") or "").strip(),
            "part_manuf": (r.get("Part_Manuf") or "").strip(),
        })
    return rows


async def _create_run_from_rows(
    db, filename: str, rows: list[dict], batch_size: int = 10, concurrency: int = 3
) -> PipelineRun:
    run = PipelineRun(filename=filename, total_items=len(rows))
    db.add(run)
    await db.flush()
    for r in rows:
        db.add(CatalogItem(
            run_id=run.id,
            row_index=r["row_index"],
            mfg_part_number=r["mfg_part_num"],
            part_desc_raw=r["part_desc"],
            e1_brand_raw="" if is_placeholder(r["e1_brand"]) else r["e1_brand"],
            unilog_brand_raw=r["unilog_brand"],
            dib_brand_raw="" if is_placeholder(r["dib_brand"]) else r["dib_brand"],
            part_manuf_raw=r["part_manuf"],
        ))
    await db.commit()
    return run


@router.post("/upload")
async def upload_catalog(
    background: BackgroundTasks,
    file: UploadFile = File(...),
    limit: int = Query(default=0, ge=0, le=10000, description="Cap rows processed (0 = all)"),
):
    """Upload the raw catalog CSV and start an enrichment pipeline run."""
    if not file.filename or not file.filename.lower().endswith((".csv", ".txt")):
        raise HTTPException(400, "Upload a CSV catalog file")
    raw = (await file.read()).decode("utf-8-sig", errors="replace")
    rows = _parse_csv_rows(raw)
    if not rows:
        raise HTTPException(400, "No data rows found in file")
    if limit:
        rows = rows[:limit]

    async for db in get_db():
        run = await _create_run_from_rows(db, file.filename, rows)
        break
    background.add_task(run_pipeline, run.id)
    return {"run_id": run.id, "items": len(rows), "status": run.status}


@router.post("/sample")
async def run_sample_dataset(
    background: BackgroundTasks,
    limit: int = Query(default=12, ge=1, le=1000),
):
    """Start a demo run from the bundled UniHack sample dataset."""
    text = SAMPLE_CSV.read_text(encoding="utf-8-sig", errors="replace")
    rows = _parse_csv_rows(text)[:limit]
    async for db in get_db():
        run = await _create_run_from_rows(db, f"sample:{SAMPLE_CSV.name}", rows)
        break
    background.add_task(run_pipeline, run.id)
    return {"run_id": run.id, "items": len(rows), "status": run.status}


@router.get("")
async def list_runs(limit: int = 20):
    async for db in get_db():
        res = await db.execute(
            select(PipelineRun).order_by(desc(PipelineRun.created_at)).limit(limit)
        )
        runs = res.scalars().all()
        return [
            {
                "id": r.id,
                "filename": r.filename,
                "total_items": r.total_items,
                "processed_items": r.processed_items,
                "failed_items": r.failed_items,
                "status": r.status,
                "stats": r.stats,
                "error_message": r.error_message,
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "completed_at": r.completed_at.isoformat() if r.completed_at else None,
            }
            for r in runs
        ]


@router.get("/{run_id}")
async def get_run(run_id: str):
    async for db in get_db():
        run = await db.get(PipelineRun, run_id)
        if not run:
            raise HTTPException(404, "Run not found")
        res = await db.execute(
            select(CatalogItem.status, func.count())
            .where(CatalogItem.run_id == run_id)
            .group_by(CatalogItem.status)
        )
        status_counts = dict(res.all())
        return {
            "id": run.id,
            "filename": run.filename,
            "total_items": run.total_items,
            "processed_items": run.processed_items,
            "failed_items": run.failed_items,
            "status": run.status,
            "stats": run.stats,
            "status_counts": status_counts,
            "error_message": run.error_message,
            "created_at": run.created_at.isoformat() if run.created_at else None,
            "started_at": run.started_at.isoformat() if run.started_at else None,
            "completed_at": run.completed_at.isoformat() if run.completed_at else None,
        }


# ---------------------------------------------------------------------------
# Catalog items
# ---------------------------------------------------------------------------

items_router = APIRouter(prefix="/items", tags=["items"])

ITEM_SUMMARY_COLS = (
    CatalogItem.id, CatalogItem.run_id, CatalogItem.row_index,
    CatalogItem.mfg_part_number, CatalogItem.part_desc_raw,
    CatalogItem.brand_name, CatalogItem.manufacturer_name,
    CatalogItem.product_name, CatalogItem.classpath, CatalogItem.fine,
    CatalogItem.ai_confidence, CatalogItem.quality_score,
    CatalogItem.needs_review, CatalogItem.status,
)


@items_router.get("")
async def list_items(
    run_id: Optional[str] = None,
    q: Optional[str] = None,
    status: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=200),
):
    async for db in get_db():
        stmt = select(*ITEM_SUMMARY_COLS)
        if run_id:
            stmt = stmt.where(CatalogItem.run_id == run_id)
        if q:
            like = f"%{q}%"
            stmt = stmt.where(or_(
                CatalogItem.mfg_part_number.ilike(like),
                CatalogItem.part_desc_raw.ilike(like),
                CatalogItem.product_name.ilike(like),
                CatalogItem.brand_name.ilike(like),
            ))
        if status:
            stmt = stmt.where(CatalogItem.status == status)

        total = await db.execute(select(func.count()).select_from(stmt.subquery()))
        count = total.scalar_one()

        res = await db.execute(
            stmt.order_by(CatalogItem.row_index)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        keys = [
            "id", "run_id", "row_index", "mfg_part_number", "part_desc_raw",
            "brand_name", "manufacturer_name", "product_name", "classpath",
            "fine", "ai_confidence", "quality_score", "needs_review", "status",
        ]
        return {"total": count, "page": page, "page_size": page_size,
                "items": [dict(zip(keys, row)) for row in res.all()]}


@items_router.get("/{item_id}")
async def get_item(item_id: str):
    async for db in get_db():
        item = await db.get(CatalogItem, item_id)
        if not item:
            raise HTTPException(404, "Item not found")
        return _serialize_item(item)


@items_router.patch("/{item_id}")
async def edit_item(item_id: str, body: dict):
    """Human manual override of any enriched field (provenance source=human)."""
    allowed = {
        "brand_name", "trade_name", "manufacturer_name", "dept", "item_class",
        "fine", "classpath", "unspsc", "product_name", "short_desc",
        "invoice_desc", "mobile_desc", "long_desc", "retail_desc",
        "marketing_description", "applications", "includes",
        "standards_approvals", "features", "attributes",
    }
    async for db in get_db():
        item = await db.get(CatalogItem, item_id)
        if not item:
            raise HTTPException(404, "Item not found")
        prov = dict(item.provenance or {})
        for key, value in body.items():
            if key not in allowed:
                continue
            setattr(item, key, value)
            prov[key] = {
                "source": "human", "confidence": 1.0,
                "method": "manual editor override",
            }
        item.provenance = prov
        if item.needs_review and item.status == "needs_review":
            item.status = "enriched"
            item.needs_review = False
        await db.commit()
        return _serialize_item(item)


@items_router.post("/{item_id}/accept")
async def accept_item(item_id: str, body: dict = None):
    """Human accepts the current record as-is — clears review state."""
    async for db in get_db():
        item = await db.get(CatalogItem, item_id)
        if not item:
            raise HTTPException(404, "Item not found")
        item.status = "enriched"
        item.needs_review = False
        prov = dict(item.provenance or {})
        prov["_record_review"] = {
            "source": "human",
            "confidence": 1.0,
            "method": "Record accepted as-is by analyst",
        }
        item.provenance = prov
        await db.commit()
        return _serialize_item(item)


def _serialize_item(item: CatalogItem) -> dict:
    quality = item.quality_checks or {}
    return {
        "id": item.id,
        "run_id": item.run_id,
        "row_index": item.row_index,
        "raw_input": {
            "mfg_part_number": item.mfg_part_number,
            "part_desc": item.part_desc_raw,
            "e1_brand": item.e1_brand_raw,
            "unilog_brand": item.unilog_brand_raw,
            "dib_brand": item.dib_brand_raw,
            "part_manuf": item.part_manuf_raw,
        },
        "manufacturer_name": item.manufacturer_name,
        "brand_name": item.brand_name,
        "trade_name": item.trade_name,
        "manufacturer_part_number": item.manufacturer_part_number,
        "taxonomy": {
            "dept": item.dept, "class": item.item_class, "fine": item.fine,
            "classpath": item.classpath, "unspsc": item.unspsc,
        },
        "descriptions": {
            "product_name": item.product_name,
            "short_desc": item.short_desc,
            "invoice_desc": item.invoice_desc,
            "mobile_desc": item.mobile_desc,
            "long_desc": item.long_desc,
            "retail_desc": item.retail_desc,
            "marketing_description": item.marketing_description,
        },
        "features": item.features or [],
        "attributes": item.attributes or [],
        "applications": item.applications,
        "includes": item.includes,
        "standards_approvals": item.standards_approvals,
        "provenance": item.provenance or {},
        "ai_confidence": item.ai_confidence,
        "quality_score": item.quality_score,
        "quality_checks": quality.get("checks", []),
        "review_flags": quality.get("flags", []),
        "needs_review": item.needs_review,
        "status": item.status,
        "error_message": item.error_message,
    }
