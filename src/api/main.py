from fastapi import FastAPI
from datetime import datetime

app = FastAPI(
    title="EU AI Act Governance Platform",
    description="Automated compliance platform for EU AI Act, GDPR, and NIST AI RMF",
    version="0.1.0"
)

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
        "health": "/health"
    }