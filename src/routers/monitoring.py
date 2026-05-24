from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional
from src.database.connection import SessionLocal
from src.database.models import MonitoringSource, RegulatoryUpdate, User
from src.monitoring.regulatory_monitor import check_all_sources, seed_monitoring_sources
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/monitoring", tags=["Regulatory Monitoring"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user_optional(db: Session = Depends(get_db)) -> Optional[User]:
    """Returns current user if authenticated, None otherwise."""
    return None


class AddSourceRequest(BaseModel):
    url: str
    title: str


@router.post("/check")
def trigger_monitoring_check():
    """
    Manually trigger a check of all monitored regulatory sources.
    Scrapes each URL, detects changes, updates knowledge base, emails admins.
    This can take 30-60 seconds as it scrapes multiple websites.
    """
    try:
        result = check_all_sources()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sources")
def list_monitoring_sources(db: Session = Depends(get_db)):
    """
    List all URLs being monitored for regulatory changes.
    Shows last checked time and whether changes were ever detected.
    """
    sources = db.query(MonitoringSource).filter(
        MonitoringSource.is_active == True
    ).all()

    return [
        {
            "id": s.id,
            "title": s.title,
            "url": s.url,
            "last_checked": s.last_checked.isoformat() if s.last_checked else None,
            "last_changed": s.last_changed.isoformat() if s.last_changed else None,
            "is_active": s.is_active
        }
        for s in sources
    ]


@router.get("/updates")
def list_regulatory_updates(db: Session = Depends(get_db)):
    """
    List all detected regulatory changes, newest first.
    Shows the AI-generated summary and how many knowledge base chunks were added.
    """
    updates = db.query(RegulatoryUpdate).order_by(
        RegulatoryUpdate.detected_at.desc()
    ).limit(50).all()

    return [
        {
            "id": u.id,
            "source_title": u.source_title,
            "source_url": u.source_url,
            "change_summary": u.change_summary,
            "chunks_added": u.chunks_added,
            "admins_notified": u.admins_notified,
            "detected_at": u.detected_at.isoformat() if u.detected_at else None
        }
        for u in updates
    ]


@router.post("/sources")
def add_monitoring_source(request: AddSourceRequest, db: Session = Depends(get_db)):
    """
    Add a new URL to the monitoring list.
    Use this to add new EUR-Lex pages, EU AI Office guidance documents, etc.
    """
    existing = db.query(MonitoringSource).filter(
        MonitoringSource.url == request.url
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="This URL is already being monitored")

    source = MonitoringSource(
        url=request.url,
        title=request.title,
        is_active=True
    )
    db.add(source)
    db.commit()
    db.refresh(source)

    return {
        "id": source.id,
        "title": source.title,
        "url": source.url,
        "message": "Source added. It will be checked on the next monitoring run."
    }