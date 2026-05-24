from src.routers.auth import verify_token
from datetime import datetime
from src.database.models import User
from fastapi.responses import FileResponse
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from src.database.connection import get_db
from src.models.schemas import (
    ClassificationRequest,
    ClassificationResponse,
    DPIARequest,
    DPIAResponse,
    OWASPRequest,
    OWASPResponse,
    FullAssessmentRequest,
    FullAssessmentResponse,
    NVDCheckRequest,
    NVDCheckResponse,
    ATLASCheckRequest,
    ATLASCheckResponse
)
from src.governance.classifier import classify_ai_system
from src.governance.dpia import generate_dpia
from src.governance.owasp import check_owasp_llm
from src.governance.nist import map_to_nist
from src.reports.audit_pdf import generate_audit_pdf
from src.database.models import AuditLedger
from src.governance.pdf_generator import generate_pdf_report
from src.governance.nvd_checker import check_technologies_nvd
from src.governance.atlas_checker import assess_atlas_risks
from src.database.models import AssessmentHistory
from src.metrics import (
    assessments_total,
    risk_tier_total,
    dpia_generated_total,
    owasp_checks_total,
    pdf_reports_total
)
import uuid
import os
import hashlib
import hmac
import json


def _write_audit_record(db, action: str, system_name: str, payload: dict):
    last = db.query(AuditLedger).order_by(AuditLedger.id.desc()).first()
    previous_hash = last.record_hash if last else "0" * 64
    payload_json = json.dumps(payload, default=str, sort_keys=True)
    content = previous_hash + payload_json
    record_hash = hashlib.sha256(content.encode()).hexdigest()
    secret = os.getenv("JWT_SECRET", "fallback-secret")
    signature = hmac.new(secret.encode(), record_hash.encode(), hashlib.sha256).hexdigest()
    record = AuditLedger(
        action=action,
        system_name=system_name,
        payload=payload_json,
        previous_hash=previous_hash,
        record_hash=record_hash,
        signature=signature
    )
    db.add(record)
    db.commit()


router = APIRouter(prefix="/api/v1", tags=["Governance"])


@router.post("/atlas-check", response_model=ATLASCheckResponse)
async def atlas_check_endpoint(request: ATLASCheckRequest):
    try:
        assessment = await assess_atlas_risks(
            system_name=request.system_name,
            uses_llm=request.uses_llm,
            accepts_user_input=request.accepts_user_input,
            has_external_api=request.has_external_api,
            processes_personal_data=request.processes_personal_data,
            automated_decision=request.automated_decision
        )
        return ATLASCheckResponse(
            system_name=assessment.system_name,
            techniques_found=len(assessment.relevant_techniques),
            tactics_covered=assessment.tactics_covered,
            risk_summary=assessment.risk_summary,
            recommendations=assessment.recommendations,
            technique_details=[
                f"{t.technique_id} — {t.name}: {t.description}"
                for t in assessment.relevant_techniques
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/nvd-check", response_model=NVDCheckResponse)
async def nvd_check_endpoint(request: NVDCheckRequest):
    try:
        assessment = await check_technologies_nvd(
            request.system_name,
            request.technologies
        )
        return NVDCheckResponse(
            system_name=assessment.system_name,
            technologies_checked=assessment.technologies_checked,
            critical_count=assessment.critical_count,
            high_count=assessment.high_count,
            medium_count=assessment.medium_count,
            overall_risk=assessment.overall_risk,
            recommendations=assessment.recommendations
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/classify", response_model=ClassificationResponse)
async def classify_endpoint(
    request: ClassificationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_token)
):
    try:
        result = classify_ai_system(request, db)

        history = AssessmentHistory(
            system_name=result.system_name,
            sector=request.sector.value,
            risk_tier=result.risk_tier.value,
            dpia_required=result.dpia_required,
            justification=result.justification,
            user_id=current_user.id,
            org_id=current_user.org_id
        )
        db.add(history)
        db.commit()

        _write_audit_record(db, "classification", result.system_name, {
            "risk_tier": result.risk_tier.value,
            "sector": request.sector.value,
            "dpia_required": result.dpia_required,
            "user_id": current_user.id,
            "org_id": current_user.org_id
        })

        assessments_total.inc()
        risk_tier_total.labels(tier=result.risk_tier.value).inc()

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dpia", response_model=DPIAResponse)
async def dpia_endpoint(request: DPIARequest):
    try:
        result = generate_dpia(request)
        dpia_generated_total.inc()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/owasp-check", response_model=OWASPResponse)
async def owasp_endpoint(request: OWASPRequest):
    try:
        result = check_owasp_llm(request)
        owasp_checks_total.inc()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/assess-and-download")
async def assess_and_download(request: FullAssessmentRequest, db: Session = Depends(get_db)):
    try:
        class_req = ClassificationRequest(
            system_name=request.system_name,
            description=request.description,
            sector=request.sector,
            automated_decision=request.automated_decision,
            processes_personal_data=request.processes_personal_data,
            interacts_with_humans=request.interacts_with_humans
        )
        classification = classify_ai_system(class_req, db)

        dpia_req = DPIARequest(
            system_name=request.system_name,
            description=request.description,
            sector=request.sector,
            data_subjects=request.data_subjects or "Not specified",
            data_types=request.data_types or "Not specified",
            processing_purpose=request.processing_purpose or "Not specified",
            risk_tier=classification.risk_tier
        )
        dpia = generate_dpia(dpia_req)

        owasp_req = OWASPRequest(
            system_name=request.system_name,
            description=request.description,
            uses_llm=request.uses_llm,
            accepts_user_input=request.accepts_user_input,
            produces_output_used_in_decisions=request.automated_decision,
            has_access_to_external_systems=False
        )
        owasp = check_owasp_llm(owasp_req)

        nist = map_to_nist(request.system_name, classification, owasp)

        filepath = generate_pdf_report(
            request.system_name,
            classification,
            dpia,
            owasp,
            nist
        )

        assessments_total.inc()
        risk_tier_total.labels(tier=classification.risk_tier.value).inc()
        dpia_generated_total.inc()
        owasp_checks_total.inc()
        pdf_reports_total.inc()

        return FileResponse(
            path=filepath,
            media_type="application/pdf",
            filename=f"{request.system_name.replace(' ', '_')}_compliance_report.pdf"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports/{report_id}")
async def get_report(report_id: str):
    return {"message": f"Report {report_id} — file serving will be implemented in Sprint 5"}


@router.get("/history")
def get_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_token)
):
    records = db.query(AssessmentHistory).filter(
        AssessmentHistory.org_id == current_user.org_id
    ).order_by(
        AssessmentHistory.assessed_at.desc()
    ).limit(50).all()
    return [
        {
            "id": r.id,
            "system_name": r.system_name,
            "sector": r.sector,
            "risk_tier": r.risk_tier,
            "dpia_required": r.dpia_required,
            "justification": r.justification,
            "assessed_at": r.assessed_at.isoformat()
        }
        for r in records
    ]


@router.get("/audit/export")
def export_audit_trail(
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_token)
):
    records = db.query(AuditLedger).order_by(AuditLedger.id.asc()).all()

    if not records:
        raise HTTPException(
            status_code=404,
            detail="No audit records found. Run some compliance assessments first."
        )

    org_name = "EU AI Act Governance Platform"
    if hasattr(current_user, 'org_id') and current_user.org_id:
        from src.database.models import Organisation
        org = db.query(Organisation).filter(Organisation.id == current_user.org_id).first()
        if org:
            org_name = org.name

    filepath = generate_audit_pdf(
        records=records,
        org_name=org_name,
        output_dir="src/reports"
    )

    return FileResponse(
        path=filepath,
        media_type="application/pdf",
        filename=f"audit_trail_{datetime.now().strftime('%Y%m%d')}.pdf",
        headers={"Content-Disposition": "attachment; filename=audit_trail.pdf"}
    )