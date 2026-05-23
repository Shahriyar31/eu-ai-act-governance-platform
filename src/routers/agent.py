from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from src.agents.compliance_agent import compliance_agent

router = APIRouter(prefix="/api/v1/agent", tags=["Compliance Agent"])


class AgentRequest(BaseModel):
    system_name: str
    description: str
    sector: str = "other"
    automated_decision: bool = False
    processes_personal_data: bool = False
    interacts_with_humans: bool = False
    uses_llm: bool = False
    accepts_user_input: bool = False


class AgentResponse(BaseModel):
    system_name: str
    risk_tier: str
    dpia_required: bool
    steps_completed: list
    final_summary: str
    dpia_assessment: Optional[dict] = None
    owasp_assessment: Optional[dict] = None


@router.post("/assess", response_model=AgentResponse)
def run_compliance_agent(request: AgentRequest):
    """
    Run the full compliance workflow agent.
    Automatically determines which assessments to run based on risk tier.
    Returns a complete compliance report in one API call.
    """
    try:
        initial_state = {
            "system_name": request.system_name,
            "description": request.description,
            "sector": request.sector,
            "automated_decision": request.automated_decision,
            "processes_personal_data": request.processes_personal_data,
            "interacts_with_humans": request.interacts_with_humans,
            "uses_llm": request.uses_llm,
            "accepts_user_input": request.accepts_user_input,
            "risk_tier": "",
            "dpia_required": False,
            "classification_justification": "",
            "classification_obligations": [],
            "dpia_assessment": None,
            "owasp_assessment": None,
            "final_summary": "",
            "steps_completed": []
        }

        result = compliance_agent.invoke(initial_state)

        return AgentResponse(
            system_name=result["system_name"],
            risk_tier=result["risk_tier"],
            dpia_required=result["dpia_required"],
            steps_completed=result["steps_completed"],
            final_summary=result["final_summary"],
            dpia_assessment=result.get("dpia_assessment"),
            owasp_assessment=result.get("owasp_assessment")
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))