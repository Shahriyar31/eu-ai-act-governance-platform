from src.routers.auth import verify_token
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
from src.governance.pdf_generator import generate_pdf_report
from src.governance.nvd_checker import check_technologies_nvd
from src.governance.atlas_checker import assess_atlas_risks
from src.database.models import AssessmentHistory
from src.api.metrics import classification_counter, dpia_counter, owasp_counter, pdf_counter
from src.governance.ledger_service import append_audit_entry, verify_audit_ledger
import uuid

router = APIRouter(prefix="", tags=["Governance"])


@router.post("/atlas-check", response_model=ATLASCheckResponse)
async def atlas_check_endpoint(request: ATLASCheckRequest, db: Session = Depends(get_db)):
    try:
        assessment = await assess_atlas_risks(
            system_name=request.system_name,
            uses_llm=request.uses_llm,
            accepts_user_input=request.accepts_user_input,
            has_external_api=request.has_external_api,
            processes_personal_data=request.processes_personal_data,
            automated_decision=request.automated_decision
        )
        
        # Append cryptographic audit ledger entry
        append_audit_entry(
            db=db,
            action="ATLAS_CHECK",
            system_name=assessment.system_name,
            payload_data={
                "request": {
                    "system_name": request.system_name,
                    "uses_llm": request.uses_llm,
                    "accepts_user_input": request.accepts_user_input,
                    "has_external_api": request.has_external_api,
                    "processes_personal_data": request.processes_personal_data,
                    "automated_decision": request.automated_decision
                },
                "response": {
                    "techniques_found": len(assessment.relevant_techniques),
                    "tactics_covered": assessment.tactics_covered,
                    "risk_summary": assessment.risk_summary,
                    "recommendations": assessment.recommendations
                }
            }
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
async def nvd_check_endpoint(request: NVDCheckRequest, db: Session = Depends(get_db)):
    try:
        assessment = await check_technologies_nvd(
            request.system_name,
            request.technologies
        )
        
        # Append cryptographic audit ledger entry
        append_audit_entry(
            db=db,
            action="NVD_CHECK",
            system_name=assessment.system_name,
            payload_data={
                "request": {
                    "system_name": request.system_name,
                    "technologies": request.technologies
                },
                "response": {
                    "technologies_checked": assessment.technologies_checked,
                    "critical_count": assessment.critical_count,
                    "high_count": assessment.high_count,
                    "medium_count": assessment.medium_count,
                    "overall_risk": assessment.overall_risk,
                    "recommendations": assessment.recommendations
                }
            }
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
            user_id=current_user.id
        )
        db.add(history)
        db.commit()
        
        # Append cryptographic audit ledger entry
        append_audit_entry(
            db=db,
            action="CLASSIFY_AI",
            system_name=result.system_name,
            payload_data={
                "request": {
                    "system_name": request.system_name,
                    "description": request.description,
                    "sector": request.sector.value,
                    "automated_decision": request.automated_decision,
                    "processes_personal_data": request.processes_personal_data,
                    "interacts_with_humans": request.interacts_with_humans
                },
                "response": {
                    "risk_tier": result.risk_tier.value,
                    "justification": result.justification,
                    "obligations": result.obligations,
                    "dpia_required": result.dpia_required
                }
            }
        )
        
        # Increment custom Prometheus metric for classification
        classification_counter.labels(
            risk_tier=result.risk_tier.value,
            sector=request.sector.value
        ).inc()
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dpia", response_model=DPIAResponse)
async def dpia_endpoint(request: DPIARequest, db: Session = Depends(get_db)):
    try:
        result = generate_dpia(request)
        
        # Append cryptographic audit ledger entry
        append_audit_entry(
            db=db,
            action="GENERATE_DPIA",
            system_name=result.system_name,
            payload_data={
                "request": {
                    "system_name": request.system_name,
                    "description": request.description,
                    "sector": request.sector.value,
                    "data_subjects": request.data_subjects,
                    "data_types": request.data_types,
                    "processing_purpose": request.processing_purpose,
                    "risk_tier": request.risk_tier.value
                },
                "response": {
                    "dpia_required": result.dpia_required,
                    "assessment_summary": result.assessment_summary,
                    "risks_identified": result.risks_identified,
                    "mitigation_measures": result.mitigation_measures,
                    "recommendation": result.recommendation
                }
            }
        )
        
        # Increment custom Prometheus metric for DPIA generation
        dpia_counter.labels(risk_tier=request.risk_tier.value).inc()
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/owasp-check", response_model=OWASPResponse)
async def owasp_endpoint(request: OWASPRequest, db: Session = Depends(get_db)):
    try:
        result = check_owasp_llm(request)
        
        # Append cryptographic audit ledger entry
        append_audit_entry(
            db=db,
            action="OWASP_CHECK",
            system_name=result.system_name,
            payload_data={
                "request": {
                    "system_name": request.system_name,
                    "description": request.description,
                    "uses_llm": request.uses_llm,
                    "accepts_user_input": request.accepts_user_input,
                    "produces_output_used_in_decisions": request.produces_output_used_in_decisions,
                    "has_access_to_external_systems": request.has_access_to_external_systems
                },
                "response": {
                    "risks_found": result.risks_found,
                    "severity_level": result.severity_level,
                    "recommendations": result.recommendations
                }
            }
        )
        
        # Increment custom Prometheus metric for OWASP LLM check
        owasp_counter.labels(uses_llm=str(request.uses_llm)).inc()
        
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
            nist,
            language=getattr(request, "language", "en")
        )

        # Append cryptographic audit ledger entry representing the full PDF certificate generation
        append_audit_entry(
            db=db,
            action="FULL_ASSESSMENT_PDF",
            system_name=request.system_name,
            payload_data={
                "system_name": request.system_name,
                "description": request.description,
                "sector": request.sector.value,
                "classification": {
                    "risk_tier": classification.risk_tier.value,
                    "dpia_required": classification.dpia_required,
                    "justification": classification.justification
                },
                "dpia": {
                    "assessment_summary": dpia.assessment_summary,
                    "risks_identified": dpia.risks_identified,
                    "mitigation_measures": dpia.mitigation_measures,
                    "recommendation": dpia.recommendation
                },
                "owasp": {
                    "risks_found": owasp.risks_found,
                    "severity_level": owasp.severity_level,
                    "recommendations": owasp.recommendations
                }
            }
        )

        # Increment custom Prometheus metric for PDF downloads
        pdf_counter.labels(system_name=request.system_name).inc()

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
        AssessmentHistory.user_id == current_user.id
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


@router.get("/verify-ledger")
def verify_ledger_endpoint(db: Session = Depends(get_db)):
    """
    Exposes the cryptographic audit log ledger integrity verification tool.
    Scans, verifies hash chain links, recalculates fingerprints, and validates RSA signatures.
    """
    try:
        audit_result = verify_audit_ledger(db)
        return audit_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sandbox/tamper")
def sandbox_tamper_endpoint(db: Session = Depends(get_db)):
    """
    Simulates a database breach / tamper by editing the latest block in place.
    """
    latest = db.query(AuditLedger).order_by(AuditLedger.id.desc()).first()
    if not latest:
        raise HTTPException(status_code=400, detail="No ledger records exist yet. Please perform a classification first!")
    
    if not latest.system_name.endswith(" (TAMPERED)"):
        latest.system_name = latest.system_name + " (TAMPERED)"
        db.commit()
        
    return {"status": "Tamper injected successfully!", "corrupted_id": latest.id}


@router.post("/sandbox/restore")
def sandbox_restore_endpoint(db: Session = Depends(get_db)):
    """
    Heals the ledger by restoring all tampered fields back to their original state.
    """
    rows = db.query(AuditLedger).all()
    healed_count = 0
    for row in rows:
        if row.system_name.endswith(" (TAMPERED)"):
            row.system_name = row.system_name.replace(" (TAMPERED)", "")
            healed_count += 1
            
    db.commit()
    return {"status": f"Ledger self-healed successfully! {healed_count} blocks restored."}


@router.post("/sandbox/traffic")
def sandbox_traffic_endpoint(db: Session = Depends(get_db)):
    """
    Simulates high-traffic auditing by inserting 5 randomized compliant transactions.
    """
    import random
    MOCK_SYSTEMS = [
        ("MedSentry Diagnostics", "healthcare", "minimal"),
        ("ResumeRanker HR", "employment", "high"),
        ("SmartGrades Evaluator", "education", "limited"),
        ("CreditScore AI", "finance", "high"),
        ("SafeDrive Autonomous", "critical_infrastructure", "high")
    ]
    for _ in range(5):
        sys_name, sector, risk = random.choice(MOCK_SYSTEMS)
        payload = {
            "system_name": sys_name,
            "description": f"Automated assessment running under {sector}.",
            "sector": sector,
            "risk_tier": risk,
            "dpia_required": risk == "high",
            "justification": f"System deployed in regulated {sector} sector."
        }
        append_audit_entry(
            db=db,
            action="FULL_ASSESSMENT_PDF",
            system_name=sys_name,
            payload_data=payload
        )
    return {"status": "5 compliance transactions successfully signed and chained!"}


