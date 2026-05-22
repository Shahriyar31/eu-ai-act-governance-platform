from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from prometheus_fastapi_instrumentator import Instrumentator

# Import counters from dedicated metrics module — not defined here anymore
from src.metrics import assessments_total, risk_tier_total
from src.routers.governance import router as governance_router
from src.routers.admin import router as admin_router
from src.routers.ai import router as ai_router
from src.routers.auth import router as auth_router
from src.database.init_db import init_db

import logging
import sys
from pythonjsonlogger import jsonlogger

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    handler = logging.StreamHandler(sys.stdout)
    
    formatter = jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%SZ"
    )
    handler.setFormatter(formatter)
    logger.handlers = [handler]
    return logging.getLogger(__name__)

logger = setup_logging()

@asynccontextmanager
async def lifespan(app):
    init_db()
    logger.info("Application started", extra={"service": "eu-ai-governance"})
    yield

app = FastAPI(
    title="EU AI Act Governance Platform",
    description="Automated compliance platform for EU AI Act, GDPR, and NIST AI RMF",
    version="0.1.0",
    lifespan=lifespan
)

# Hooks into every request and exposes /metrics endpoint
Instrumentator().instrument(app).expose(app)

app.include_router(governance_router)
app.include_router(admin_router)
app.include_router(ai_router)
app.include_router(auth_router)

@app.get("/health")
def health_check():
    logger.info("Health check requested")
    return {
        "status": "healthy",
        "service": "EU AI Act Governance Platform",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

FRONTEND_DIST = Path(__file__).parent.parent.parent / "frontend" / "dist"
if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

    @app.get("/")
    def serve_frontend():
        return FileResponse(FRONTEND_DIST / "index.html")

    @app.get("/{full_path:path}")
    def serve_spa(full_path: str):
        file_path = FRONTEND_DIST / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(FRONTEND_DIST / "index.html")
else:
    @app.get("/")
    def root():
        return {
            "message": "EU AI Act Governance Platform API",
            "docs": "/docs",
            "health": "/health"
        }