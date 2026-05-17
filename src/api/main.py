from fastapi import FastAPI
from datetime import datetime
from src.routers.governance import router as governance_router
from src.routers.admin import router as admin_router

app = FastAPI(
    title="EU AI Act Governance Platform",
    description="Automated compliance platform for EU AI Act, GDPR, and NIST AI RMF",
    version="0.1.0"
)

app.include_router(governance_router)
app.include_router(admin_router)

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "EU AI Act Governance Platform",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/")
def root():
    return {
        "message": "EU AI Act Governance Platform API",
        "docs": "/docs",
        "health": "/health",
        "assess": "/api/v1/assess"
    }