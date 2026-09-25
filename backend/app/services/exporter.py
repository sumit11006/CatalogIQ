"""Delivery-format exporter — emits the exact 252-column Unilog delivery CSV."""

import csv
import io
from pathlib import Path
from typing import Any

from app.models.catalog import CatalogItem

_TEMPLATE_PATH = Path(__file__).resolve().parent.parent / "assets" / "delivery_format_template.csv"

_HEADER_CACHE: list[str] | None = None


def get_delivery_header() -> list[str]:
    """Load the exact column order from the shipped template (cached)."""
    global _HEADER_CACHE
    if _HEADER_CACHE is None:
        with open(_TEMPLATE_PATH, newline="", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            _HEADER_CACHE = next(reader)
    return list(_HEADER_CACHE)


def build_delivery_row(item: CatalogItem) -> dict[str, str]:
    """Map an enriched CatalogItem onto the 252-column schema."""
    attrs = item.attributes or []
    features = item.features or []
    row: dict[str, str] = {}

    def put(col: str, val: Any) -> None:
        if val is None:
            return
        row[col] = str(val)

    # raw passthrough
    put("PART_NUMBER", item.mfg_part_number)
    put("Mfg_Part_Num", item.mfg_part_number)
    put("Part_Desc", item.part_desc_raw)
    put("E1_Brand", item.e1_brand_raw)
    put("Unilog_Brand", item.unilog_brand_raw)
    put("DIB_Brand", item.dib_brand_raw)
    put("Part_Manuf", item.part_manuf_raw)

    # identity & taxonomy
    put("MANUFACTURER_NAME", item.manufacturer_name)
    put("BRAND_NAME", item.brand_name)
    put("TRADE_NAME", item.trade_name)
    put("MANUFACTURER_PART_NUMBER", item.manufacturer_part_number or item.mfg_part_number)
    put("Classpath", item.classpath)
    put("Dept", item.dept)
    put("Class", item.item_class)
    put("Fine", item.fine)
    put("UNSPSC", item.unspsc)

    # descriptions
    put("Product Name", item.product_name)
    put("SHORT_DESC", item.short_desc)
    put("MOBILE_DESC", item.mobile_desc)
    put("INVOICE_DESC", item.invoice_desc)
    put("LONG_DESC1", item.long_desc)
    put("RETAIL_DESC", item.retail_desc)
    put("MARKETING_DESCRIPTION", item.marketing_description)

    for i, feat in enumerate(features[:20], start=1):
        put(f"ITEM_FEATURES_{i}", feat)

    put("Standard/Approvals", item.standards_approvals)
    put("Application", item.applications)
    put("Includes", item.includes)

    for i, attr in enumerate(attrs[:50], start=1):
        put(f"ATTRIBUTE_LABEL {i}", attr.get("label"))
        put(f"ATTRIBUTE_VALUE {i}", attr.get("value"))
        put(f"ATTRIBUTE_UOM {i}", attr.get("uom"))

    return row


def items_to_csv(items: list[CatalogItem]) -> str:
    header = get_delivery_header()
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=header, extrasaction="ignore")
    writer.writeheader()
    for item in items:
        writer.writerow(build_delivery_row(item))
    return buf.getvalue()


def row_completion(row: dict[str, str], total_cols: int | None = None) -> float:
    """Calculate completeness percentage against the full 252-column schema."""
    if total_cols is None:
        try:
            total_cols = len(get_delivery_header())
        except Exception:
            total_cols = 252
    filled = sum(1 for v in row.values() if v and str(v).strip())
    return round(filled / total_cols * 100, 1) if total_cols > 0 else 0.0
