"""CatalogIQ Backend API and Rules Engine tests."""

import pytest
from httpx import AsyncClient
try:
    from httpx import ASGITransport
    HAS_ASGI_TRANSPORT = True
except ImportError:
    HAS_ASGI_TRANSPORT = False

from app.main import app
from app.database import AsyncSessionLocal, init_db
from app.services.rules_engine import (
    decimal_to_fraction,
    enforce_invoice_desc,
    enforce_mobile_desc,
    expand_abbreviations,
    is_placeholder,
    normalise_entity_case,
    normalise_uom_text,
    parse_manufacturer,
)
from app.services.quality_engine import check_quality


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session", autouse=True)
async def setup_db():
    await init_db()


@pytest.fixture
async def client():
    """Provide an async test HTTP client."""
    if HAS_ASGI_TRANSPORT:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            yield ac
    else:
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac


class TestHealth:
    async def test_health_check(self, client: AsyncClient):
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "catalogiq"
        assert "version" in data


class TestAnalytics:
    async def test_dashboard_analytics(self, client: AsyncClient):
        response = await client.get("/api/v1/analytics")
        assert response.status_code == 200
        data = response.json()
        assert "items_total" in data
        assert "by_status" in data
        assert "avg_ai_confidence" in data
        assert "avg_quality_score" in data
        assert "ai_mode" in data


class TestExport:
    async def test_export_template(self, client: AsyncClient):
        response = await client.get("/api/v1/export/template")
        assert response.status_code == 200
        data = response.json()
        assert "columns" in data
        assert data["columns"] == 252
        assert "header" in data
        assert len(data["header"]) == 252
        assert "Mfg_Part_Num" in data["header"]
        assert "INVOICE_DESC" in data["header"]

    async def test_export_csv_empty_or_all(self, client: AsyncClient):
        response = await client.get("/api/v1/export/csv")
        assert response.status_code == 200
        assert "text/csv" in response.headers.get("content-type", "")


class TestValidationAPI:
    async def test_validation_queue_and_stats(self, client: AsyncClient):
        queue_resp = await client.get("/api/v1/validation/queue")
        assert queue_resp.status_code == 200
        assert isinstance(queue_resp.json(), list)

        stats_resp = await client.get("/api/v1/validation/stats")
        assert stats_resp.status_code == 200
        data = stats_resp.json()
        assert "total" in data
        assert "pending" in data
        assert "approved" in data
        assert "rejected" in data


class TestRunsAndItems:
    async def test_sample_run_lifecycle(self, client: AsyncClient):
        # Trigger demo run with 2 rows
        post_resp = await client.post("/api/v1/runs/sample?limit=2")
        assert post_resp.status_code == 200
        run_data = post_resp.json()
        assert "run_id" in run_data
        run_id = run_data["run_id"]

        # Check run details
        run_resp = await client.get(f"/api/v1/runs/{run_id}")
        assert run_resp.status_code == 200
        assert run_resp.json()["id"] == run_id

        # List items for this run
        items_resp = await client.get(f"/api/v1/items?run_id={run_id}")
        assert items_resp.status_code == 200
        items_data = items_resp.json()
        assert "items" in items_data
        assert items_data["total"] >= 1

        if items_data["items"]:
            item_id = items_data["items"][0]["id"]
            # Get single item
            detail_resp = await client.get(f"/api/v1/items/{item_id}")
            assert detail_resp.status_code == 200
            item_detail = detail_resp.json()
            assert "raw_input" in item_detail
            assert "descriptions" in item_detail
            assert "provenance" in item_detail

            # Test PATCH item
            patch_resp = await client.patch(
                f"/api/v1/items/{item_id}",
                json={"product_name": "Updated Test Product Title"},
            )
            assert patch_resp.status_code == 200
            updated = patch_resp.json()
            assert updated["descriptions"]["product_name"] == "Updated Test Product Title"
            assert updated["provenance"]["product_name"]["source"] == "human"

            # Test Accept item
            accept_resp = await client.post(f"/api/v1/items/{item_id}/accept")
            assert accept_resp.status_code == 200
            assert accept_resp.json()["status"] == "enriched"


class TestRulesEngine:
    def test_expand_abbreviations(self):
        text, terms = expand_abbreviations("3/8 CPLG BRS 150# SS")
        assert "Coupling" in text
        assert "Brass" in text
        assert "Stainless Steel" in text
        assert "SS" in terms or "BRS" in terms

    def test_enforce_invoice_desc(self):
        long_desc = "diablo 1/2 in x 18 in sanding belt cubitron extra long description exceeding forty characters easily"
        inv = enforce_invoice_desc(long_desc)
        assert len(inv) <= 40
        assert inv.isupper()

    def test_enforce_mobile_desc(self):
        long_desc = "Diablo 1/2 in x 18 in Sanding Belt, Cubitron II Abrasive, 6 per Pack, Extra Padding and Details"
        mob = enforce_mobile_desc(long_desc)
        assert len(mob) <= 80

    def test_decimal_to_fraction(self):
        assert decimal_to_fraction(0.25) == "1/4"
        assert decimal_to_fraction(50.25) == "50-1/4"
        assert decimal_to_fraction(0.5) == "1/2"
        assert decimal_to_fraction(24.0) == "24"

    def test_normalise_uom_text(self):
        norm, applied = normalise_uom_text("24 inches by 50.25 in with 2700 kelvin")
        assert "24 in" in norm
        assert "50-1/4 in" in norm
        assert "2700 K" in norm
        assert "in" in applied or "K" in applied

    def test_parse_manufacturer(self):
        name, code = parse_manufacturer("Freud Inc (2435)")
        assert name == "Freud Inc"
        assert code == "2435"

    def test_is_placeholder(self):
        assert is_placeholder("-- Unbranded --") is True
        assert is_placeholder("-- No DIB Brand --") is True
        assert is_placeholder("-- No Unilog Brand --") is True
        assert is_placeholder("Diablo") is False

    def test_quality_checks(self):
        fields = {
            "product_name": "Diablo DCB518ASTS06G 1/2 in x 18 in Sanding Belt",
            "invoice_desc": "SANDING BELT 1/2X18 6PK",
            "mobile_desc": "Diablo 1/2 in x 18 in Sanding Belt, Cubitron II Abrasive",
            "long_desc": "Full description with 50-1/4 in length and durable construction.",
            "classpath": "Tools > Power Tool Accessories > Sanding Belts",
            "attributes": [
                {"label": "Width", "value": "1/2", "uom": "in"},
                {"label": "Length", "value": "18", "uom": "in"},
                {"label": "Grit", "value": "80", "uom": ""},
            ],
        }
        res = check_quality(fields)
        assert res["score"] >= 80
        assert res["passed_count"] >= 9
