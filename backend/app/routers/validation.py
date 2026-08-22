"""Human-in-the-loop validation queue API."""

import json
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException
from sqlalchemy import func, select

from app.database import get_db
from app.models.catalog import CatalogItem, ValidationItem

router = APIRouter(prefix="/validation", tags=["validation"])

# Where approved values land on CatalogItem
_FIELD_TO_COLUMN = {
    "dept": "dept", "item_class": "item_class", "fine": "fine",
    "classpath": "classpath", "unspsc": "unspsc",
    "brand_name": "brand_name", "trade_name": "trade_name",
    "manufacturer_name": "manufacturer_name",
    "product_name": "product_name", "short_desc": "short_desc",
    "invoice_desc": "invoice_desc", "mobile_desc": "mobile_desc",
    "long_desc": "long_desc", "marketing_description": "marketing_description",
}


def _serialize(v: ValidationItem, part_number: str | None = None,
               product_name: str | None = None) -> dict:
    return {
        "id": v.id,
        "item_id": v.item_id,
        "run_id": v.run_id,
        "field_group": v.field_group,
        "field_name": v.field_name,
        "current_value": v.current_value,
        "proposed_value": v.proposed_value,
        "reason": v.reason,
        "ai_confidence": v.ai_confidence,
        "status": v.status,
        "reviewer_note": v.reviewer_note,
        "resolved_at": v.resolved_at.isoformat() if v.resolved_at else None,
        "created_at": v.created_at.isoformat() if v.created_at else None,
        "part_number": part_number,
        "product_name": product_name,
    }


@router.get("/queue")
async def queue(
    run_id: Optional[str] = None,
    status: str = "pending",
    limit: int = 50,
):
    async for db in get_db():
        stmt = (
            select(ValidationItem, CatalogItem.mfg_part_number, CatalogItem.product_name)
            .join(CatalogItem, ValidationItem.item_id == CatalogItem.id)
            .order_by(ValidationItem.ai_confidence.asc())
            .limit(limit)
        )
        if status != "all":
            stmt = stmt.where(ValidationItem.status == status)
        if run_id:
            stmt = stmt.where(ValidationItem.run_id == run_id)
        res = await db.execute(stmt)
        return [_serialize(v, mpn, pn) for v, mpn, pn in res.all()]


@router.get("/stats")
async def stats():
    async for db in get_db():
        total = await db.execute(select(func.count()).select_from(ValidationItem))
        pending = await db.execute(
            select(func.count()).select_from(ValidationItem)
            .where(ValidationItem.status == "pending")
        )
        approved = await db.execute(
            select(func.count()).select_from(ValidationItem)
            .where(ValidationItem.status == "approved")
        )
        rejected = await db.execute(
            select(func.count()).select_from(ValidationItem)
            .where(ValidationItem.status == "rejected")
        )
        return {
            "total": total.scalar_one(),
            "pending": pending.scalar_one(),
            "approved": approved.scalar_one(),
            "rejected": rejected.scalar_one(),
        }


@router.post("/{validation_id}/action")
async def action(validation_id: str, body: dict):
    """Approve (applies value to the catalog item) or reject a proposal."""
    decision = body.get("action", "").lower()
    note = body.get("note")
    if decision not in ("approve", "reject"):
        raise HTTPException(400, "action must be 'approve' or 'reject'")

    async for db in get_db():
        v = await db.get(ValidationItem, validation_id)
        if not v:
            raise HTTPException(404, "Validation item not found")

        v.status = "approved" if decision == "approve" else "rejected"
        v.reviewer_note = note
        v.resolved_by = body.get("reviewer") or "analyst"
        v.resolved_at = datetime.now(timezone.utc)

        if decision == "approve":
            column = _FIELD_TO_COLUMN.get(v.field_name)
            item = await db.get(CatalogItem, v.item_id)
            if item and column:
                setattr(item, column, v.proposed_value)
                prov = dict(item.provenance or {})
                prov[v.field_name] = {
                    "source": "human",
                    "confidence": 1.0,
                    "method": f"HITL approval ({v.resolved_by})",
                    **({"reviewer_note": note} if note else {}),
                }
                item.provenance = prov
                item.needs_review = False
                if item.status == "needs_review":
                    # stay enriched once all flags resolved; simple heuristic here
                    remaining = await db.execute(
                        select(func.count()).select_from(ValidationItem)
                        .where(
                            ValidationItem.item_id == item.id,
                            ValidationItem.status == "pending",
                        )
                    )
                    if remaining.scalar_one() == 0:
                        item.status = "enriched"
        await db.commit()
        return {"id": v.id, "status": v.status}
