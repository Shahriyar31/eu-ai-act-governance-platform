from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from src.routers.governance import router as governance_router
from src.routers.admin import router as admin_router
from src.routers.ai import router as ai_router
from src.routers.auth import router as auth_router
from src.database.init_db import init_db

@asynccontextmanager
async def lifespan(app):
    init_db()
    yield

app = FastAPI(
    title="EU AI Act Governance Platform",
    description="Automated compliance platform for EU AI Act, GDPR, and NIST AI RMF",
    version="0.1.0",
    lifespan=lifespan
)

app.include_router(governance_router)
app.include_router(admin_router)
app.include_router(ai_router)
app.include_router(auth_router)

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "EU AI Act Governance Platform",
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
