from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from src.database.connection import get_db
from src.database.models import User, AssessmentHistory
from src.routers.auth import verify_token
from src.models.schemas import ClassificationRequest, ClassificationRequestV2, ClassificationResponseV2
from src.governance.classifier import classify_ai_system
from src.governance.ledger_service import append_audit_entry
from src.api.metrics import classification_counter

# V2 governance router (version prefix will be controlled by sub-app mount!)
router = APIRouter(tags=["Governance V2"])

@router.post("/classify", response_model=ClassificationResponseV2)
async def classify_endpoint_v2(
    request: ClassificationRequestV2,
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_token)
):
    """
    V2 AI Risk Classification Endpoint.
    Requires 'intended_purpose' field in accordance with EU AI Act Article 6 risk assessment parameters.
    Mathematically signs and appends this audit block to the cryptographic compliance ledger.
    """
    try:
        # Map the V2 request fields back to the core classifier engine model
        core_request = ClassificationRequest(
            system_name=request.system_name,
            description=request.description,
            sector=request.sector,
            automated_decision=request.automated_decision,
            processes_personal_data=request.processes_personal_data,
            interacts_with_humans=request.interacts_with_humans
        )
        
        # Execute classification logic
        result = classify_ai_system(core_request, db)
        
        # Record standard assessment history
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
        
        # Append cryptographically signed block to our compliance audit ledger!
        append_audit_entry(
            db=db,
            action="CLASSIFY_AI_V2",
            system_name=result.system_name,
            payload_data={
                "request": {
                    "system_name": request.system_name,
                    "description": request.description,
                    "intended_purpose": request.intended_purpose,
                    "sector": request.sector.value,
                    "automated_decision": request.automated_decision,
                    "processes_personal_data": request.processes_personal_data,
                    "interacts_with_humans": request.interacts_with_humans
                },
                "response": {
                    "risk_tier": result.risk_tier.value,
                    "justification": result.justification,
                    "obligations": result.obligations,
                    "dpia_required": result.dpia_required,
                    "intended_purpose": request.intended_purpose,
                    "regulatory_framework": "EU AI Act 2024 (Reg. EU 2024/1689)"
                }
            }
        )
        
        # Increment metric counters
        classification_counter.labels(
            risk_tier=result.risk_tier.value,
            sector=request.sector.value
        ).inc()
        
        return ClassificationResponseV2(
            system_name=result.system_name,
            risk_tier=result.risk_tier,
            justification=result.justification,
            obligations=result.obligations,
            dpia_required=result.dpia_required,
            intended_purpose=request.intended_purpose
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
