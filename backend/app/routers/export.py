"""Delivery-format export API."""

import io
from typing import Optional

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from sqlalchemy import select

from app.database import get_db
from app.models.catalog import CatalogItem, PipelineRun
from app.services.exporter import build_delivery_row, get_delivery_header, row_completion

router = APIRouter(prefix="/export", tags=["export"])


@router.get("/template")
async def template():
    header = get_delivery_header()
    return {"columns": len(header), "header": header}


@router.get("/preview")
async def preview(run_id: str, limit: int = 3):
    """Preview delivery rows with completion percentage."""
    async for db in get_db():
        stmt = (
            select(CatalogItem)
            .where(CatalogItem.run_id == run_id, CatalogItem.status.in_(["enriched", "needs_review", "approved"]))
            .order_by(CatalogItem.row_index)
            .limit(limit)
        )
        items = (await db.execute(stmt)).scalars().all()
        return [
            {
                "part_number": it.mfg_part_number,
                "product_name": it.product_name,
                "completion": row_completion(build_delivery_row(it)),
            }
            for it in items
        ]


@router.get("/csv")
async def export_csv(run_id: Optional[str] = None, only_enriched: bool = True):
    """Download the full delivery-format CSV for a run (or all runs)."""
    async for db in get_db():
        if run_id:
            run = await db.get(PipelineRun, run_id)
            filename = f"catalogiq_delivery_{run.filename.replace('.csv', '')}.csv" if run else "delivery.csv"
        else:
            filename = "catalogiq_delivery_full.csv"

        stmt = select(CatalogItem).order_by(CatalogItem.run_id, CatalogItem.row_index)
        conditions = []
        if run_id:
            conditions.append(CatalogItem.run_id == run_id)
        if only_enriched:
            conditions.append(CatalogItem.status.in_(["enriched", "needs_review", "approved"]))
        if conditions:
            stmt = stmt.where(*conditions)

        items = (await db.execute(stmt)).scalars().all()

        from app.services.exporter import items_to_csv

        csv_text = items_to_csv(list(items))
        return StreamingResponse(
            io.StringIO(csv_text),
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
