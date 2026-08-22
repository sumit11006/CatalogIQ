"""CatalogIQ v2 data models — Unilog-style catalog enrichment pipeline.

Pipeline: Raw CSV rows -> CatalogItem -> AI enrichment -> validation -> delivery export.
Every enriched field carries provenance (source, method, model, confidence, reasoning).
"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def new_uuid() -> str:
    return str(uuid.uuid4())


class PipelineRun(Base):
    """A batch enrichment run over an uploaded catalog file."""

    __tablename__ = "pipeline_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    filename: Mapped[str] = mapped_column(String(255))
    total_items: Mapped[int] = mapped_column(Integer, default=0)
    processed_items: Mapped[int] = mapped_column(Integer, default=0)
    failed_items: Mapped[int] = mapped_column(Integer, default=0)
    # queued | running | completed | failed | cancelled
    status: Mapped[str] = mapped_column(String(20), default="queued", index=True)
    # items/batch and concurrent batches used
    batch_size: Mapped[int] = mapped_column(Integer, default=10)
    concurrency: Mapped[int] = mapped_column(Integer, default=3)
    stats: Mapped[Optional[dict]] = mapped_column(JSON, default=None)  # aggregated metrics
    error_message: Mapped[Optional[str]] = mapped_column(Text, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), default=None)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), default=None)


class CatalogItem(Base):
    """One catalog row: raw input in, enriched delivery-ready record out."""

    __tablename__ = "catalog_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    run_id: Mapped[str] = mapped_column(String(36), ForeignKey("pipeline_runs.id"), index=True)
    row_index: Mapped[int] = mapped_column(Integer)

    # ---- Raw input (as received) ----
    mfg_part_number: Mapped[str] = mapped_column(String(120), index=True)
    part_desc_raw: Mapped[str] = mapped_column(Text, default="")
    e1_brand_raw: Mapped[str] = mapped_column(String(120), default="")
    unilog_brand_raw: Mapped[str] = mapped_column(String(120), default="")
    dib_brand_raw: Mapped[str] = mapped_column(String(120), default="")
    part_manuf_raw: Mapped[str] = mapped_column(String(160), default="")

    # ---- Pipeline state ----
    # pending | processing | enriched | needs_review | approved | failed
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)
    ai_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    quality_score: Mapped[float] = mapped_column(Float, default=0.0)  # 0-100 completeness/compliance
    needs_review: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    # ---- Normalized core identity ----
    manufacturer_name: Mapped[Optional[str]] = mapped_column(String(200), default=None)
    brand_name: Mapped[Optional[str]] = mapped_column(String(200), default=None)
    trade_name: Mapped[Optional[str]] = mapped_column(String(200), default=None)
    manufacturer_part_number: Mapped[Optional[str]] = mapped_column(String(120), default=None)

    # ---- Taxonomy ----
    dept: Mapped[Optional[str]] = mapped_column(String(120), default=None)
    item_class: Mapped[Optional[str]] = mapped_column(String(120), default=None)
    fine: Mapped[Optional[str]] = mapped_column(String(120), default=None)
    classpath: Mapped[Optional[str]] = mapped_column(Text, default=None)
    unspsc: Mapped[Optional[str]] = mapped_column(String(20), default=None)

    # ---- Descriptions (each follows a distinct formula/char limit) ----
    product_name: Mapped[Optional[str]] = mapped_column(Text, default=None)
    short_desc: Mapped[Optional[str]] = mapped_column(Text, default=None)
    invoice_desc: Mapped[Optional[str]] = mapped_column(String(60), default=None)
    mobile_desc: Mapped[Optional[str]] = mapped_column(Text, default=None)
    long_desc: Mapped[Optional[str]] = mapped_column(Text, default=None)
    retail_desc: Mapped[Optional[str]] = mapped_column(Text, default=None)
    marketing_description: Mapped[Optional[str]] = mapped_column(Text, default=None)

    # ---- Structured data ----
    features: Mapped[Optional[list]] = mapped_column(JSON, default=None)  # list[str]
    attributes: Mapped[Optional[list]] = mapped_column(JSON, default=None)
    # [{label, value, uom}]
    applications: Mapped[Optional[str]] = mapped_column(Text, default=None)
    includes: Mapped[Optional[str]] = mapped_column(Text, default=None)
    standards_approvals: Mapped[Optional[str]] = mapped_column(Text, default=None)

    # ---- Traceability & export ----
    provenance: Mapped[Optional[dict]] = mapped_column(JSON, default=None)
    # field -> {value, source: input|rule|ai|human, method, model, confidence, reasoning}
    delivery_payload: Mapped[Optional[dict]] = mapped_column(JSON, default=None)  # full 252-col dict
    quality_checks: Mapped[Optional[dict]] = mapped_column(JSON, default=None)
    # {passed: int, failed: int, issues: [str]}
    error_message: Mapped[Optional[str]] = mapped_column(Text, default=None)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )


class ValidationItem(Base):
    """Human-in-the-loop review entry for a low-confidence or flagged field."""

    __tablename__ = "validation_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    item_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("catalog_items.id"), index=True
    )
    run_id: Mapped[str] = mapped_column(String(36), index=True)

    field_group: Mapped[str] = mapped_column(String(40))  # identity|taxonomy|descriptions|attributes
    field_name: Mapped[str] = mapped_column(String(80))
    current_value: Mapped[Optional[str]] = mapped_column(Text, default=None)
    proposed_value: Mapped[Text] = mapped_column(Text)
    reason: Mapped[Optional[str]] = mapped_column(Text, default=None)  # AI rationale
    ai_confidence: Mapped[float] = mapped_column(Float, default=0.0)

    # pending | approved | rejected
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)
    reviewer_note: Mapped[Optional[str]] = mapped_column(Text, default=None)
    resolved_by: Mapped[Optional[str]] = mapped_column(String(80), default=None)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), default=None)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
