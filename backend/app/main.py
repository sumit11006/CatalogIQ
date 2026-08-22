"""CatalogIQ — AI-powered product intelligence & catalog enrichment platform."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.database import close_db, init_db
from app.routers.analytics import router as analytics_router
from app.routers.export import router as export_router
from app.routers.runs import items_router, router as runs_router
from app.routers.validation import router as validation_router
from app.utils.logger import configure_logging, get_logger

settings = get_settings()
configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    logger.info("CatalogIQ ready — Gemini AI available" )
    yield
    await close_db()


app = FastAPI(
    title="CatalogIQ API",
    description="Autonomous catalog enrichment: raw rows in, commerce-ready "
    "product records out — with traceability and human-in-the-loop review.",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1024)

API = "/api/v1"
app.include_router(runs_router, prefix=API)
app.include_router(items_router, prefix=API)
app.include_router(validation_router, prefix=API)
app.include_router(export_router, prefix=API)
app.include_router(analytics_router, prefix=API)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "catalogiq", "version": "2.0.0"}


# ---------------------------------------------------------------------------
# Serve the built frontend (single-service deployment) when dist/ exists
# ---------------------------------------------------------------------------
_frontend_dist = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"

if _frontend_dist.exists():
    app.mount("/assets", StaticFiles(directory=_frontend_dist / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def spa(full_path: str):
        """SPA fallback — serve index.html for all non-API routes."""
        if full_path and full_path != "index.html":
            candidate = _frontend_dist / full_path
            if candidate.is_file():
                return FileResponse(candidate)
        return FileResponse(_frontend_dist / "index.html")
