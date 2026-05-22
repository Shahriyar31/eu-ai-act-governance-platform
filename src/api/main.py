from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from prometheus_fastapi_instrumentator import Instrumentator
from src.routers.governance import router as governance_router
from src.routers.governance_v2 import router as governance_v2_router
from src.routers.admin import router as admin_router
from src.routers.ai import router as ai_router
from src.database.init_db import init_db
from src.routers.auth import router as auth_router


@asynccontextmanager
async def lifespan(app):
    init_db()
    yield

# Main Gateway Application (manages UI serving, health, auth, and mounts API versions)
app = FastAPI(
    title="EU AI Act Governance Gateway",
    description="Main entry gateway routing compliance traffic to isolated sub-applications.",
    version="0.1.0",
    lifespan=lifespan
)

# 1. Version 1.0 Compliance Application (Mounted at /api/v1)
v1_app = FastAPI(
    title="EU AI Act Governance API (V1)",
    description="Compliance specifications (V1) for Risk Tier Classification, GDPR DPIA, and OWASP scanners.",
    version="1.0.0"
)
v1_app.include_router(governance_router)
v1_app.include_router(ai_router)

# 2. Version 2.0 Compliance Application (Mounted at /api/v2)
v2_app = FastAPI(
    title="EU AI Act Governance API (V2)",
    description="Compliance specifications (V2) introducing 'intended_purpose' Article 6 assessment metrics.",
    version="2.0.0"
)
v2_app.include_router(governance_v2_router)

# Mount the versioned sub-apps onto the parent gateway
app.mount("/api/v1", v1_app)
app.mount("/api/v2", v2_app)

# Include shared global utilities directly on the main gateway
app.include_router(auth_router)
app.include_router(admin_router)

# Register Prometheus Instrumentator globally (automatically tracks all mounted sub-app requests!)
Instrumentator().instrument(app).expose(app)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "EU AI Act Governance Platform Gateway",
        "timestamp": datetime.utcnow().isoformat()
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
