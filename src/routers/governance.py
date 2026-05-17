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
import uuid


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
async def classify_endpoint(request: ClassificationRequest, db: Session = Depends(get_db)):
    try:
        result = classify_ai_system(request, db)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dpia", response_model=DPIAResponse)
async def dpia_endpoint(request: DPIARequest):
    try:
        result = generate_dpia(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/owasp-check", response_model=OWASPResponse)
async def owasp_endpoint(request: OWASPRequest):
    try:
        result = check_owasp_llm(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/assess", response_model=FullAssessmentResponse)
async def full_assessment_endpoint(request: FullAssessmentRequest, db: Session = Depends(get_db)):
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

        report_id = str(uuid.uuid4())
        filepath = generate_pdf_report(
            request.system_name,
            classification,
            dpia,
            owasp,
            nist
        )

        return FullAssessmentResponse(
            system_name=request.system_name,
            classification=classification,
            dpia=dpia,
            owasp=owasp,
            report_id=report_id,
            report_download_url=f"/api/v1/reports/{report_id}"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports/{report_id}")
async def get_report(report_id: str):
    return {"message": f"Report {report_id} — file serving will be implemented in Sprint 5"}