"""Analytics — pipeline health, quality and coverage KPIs for the dashboard."""

from fastapi import APIRouter
from sqlalchemy import func, select

from app.database import get_db
from app.models.catalog import CatalogItem, PipelineRun, ValidationItem
from app.services.enrichment_ai import service as ai_service

router = APIRouter(prefix="/analytics", tags=["analytics"])


async def _dashboard_payload() -> dict:
    async for db in get_db():
        items_total = await db.execute(select(func.count()).select_from(CatalogItem))
        total = items_total.scalar_one()

        status_rows = await db.execute(
            select(CatalogItem.status, func.count()).group_by(CatalogItem.status)
        )
        by_status = dict(status_rows.all())

        avg_conf = await db.execute(
            select(func.avg(CatalogItem.ai_confidence)).where(CatalogItem.ai_confidence > 0)
        )
        avg_quality = await db.execute(
            select(func.avg(CatalogItem.quality_score)).where(CatalogItem.quality_score > 0)
        )
        needs_review = await db.execute(
            select(func.count()).select_from(CatalogItem).where(CatalogItem.needs_review)
        )

        cat_rows = await db.execute(
            select(CatalogItem.dept, func.count())
            .where(CatalogItem.dept.is_not(None), CatalogItem.dept != "")
            .group_by(CatalogItem.dept)
            .order_by(func.count().desc())
            .limit(8)
        )
        top_categories = [{"name": n or "Unclassified", "count": c} for n, c in cat_rows.all()]

        brand_rows = await db.execute(
            select(CatalogItem.brand_name, func.count())
            .where(CatalogItem.brand_name.is_not(None), CatalogItem.brand_name != "")
            .group_by(CatalogItem.brand_name)
            .order_by(func.count().desc())
            .limit(8)
        )
        top_brands = [{"name": n, "count": c} for n, c in brand_rows.all()]

        val_pending = await db.execute(
            select(func.count()).select_from(ValidationItem)
            .where(ValidationItem.status == "pending")
        )
        runs_total = await db.execute(select(func.count()).select_from(PipelineRun))

        # Real engine mode — verified by actual call results, not just key presence
        if ai_service.last_status == "live":
            ai_mode = "live"
        elif ai_service.last_status == "fallback":
            ai_mode = "fallback"
        else:
            ai_mode = "ready" if ai_service.is_available else "offline"

        return {
            "items_total": total,
            "by_status": by_status,
            "avg_ai_confidence": round(avg_conf.scalar_one() or 0, 3),
            "avg_quality_score": round(avg_quality.scalar_one() or 0, 1),
            "needs_review_count": needs_review.scalar_one(),
            "pending_validations": val_pending.scalar_one(),
            "runs_total": runs_total.scalar_one(),
            "ai_mode": ai_mode,
            "top_categories": top_categories,
            "top_brands": top_brands,
        }


@router.get("")
async def dashboard():
    return await _dashboard_payload()
