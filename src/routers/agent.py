from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from uuid import uuid4
from langgraph.types import Command
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


class ClarificationResponse(BaseModel):
    status: str
    thread_id: str
    risk_tier: str
    classification_justification: str
    questions: list[str]


class RespondRequest(BaseModel):
    thread_id: str
    answers: str


@router.post("/assess")
def run_compliance_agent(request: AgentRequest):
    """
    Start a compliance assessment.
    For HIGH and LIMITED risk systems, returns clarifying questions and a thread_id.
    For MINIMAL and UNACCEPTABLE risk systems, returns the complete report immediately.
    """
    try:
        thread_id = str(uuid4())
        config = {"configurable": {"thread_id": thread_id}}

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
            "clarification_questions": [],
            "user_clarifications": None,
            "dpia_assessment": None,
            "owasp_assessment": None,
            "final_summary": "",
            "steps_completed": []
        }

        compliance_agent.invoke(initial_state, config=config)

        snapshot = compliance_agent.get_state(config)

        if snapshot.next:
            questions = []
            if snapshot.tasks and snapshot.tasks[0].interrupts:
                interrupt_value = snapshot.tasks[0].interrupts[0].value
                questions = interrupt_value if isinstance(interrupt_value, list) else [str(interrupt_value)]

            return ClarificationResponse(
                status="awaiting_clarification",
                thread_id=thread_id,
                risk_tier=snapshot.values.get("risk_tier", ""),
                classification_justification=snapshot.values.get("classification_justification", ""),
                questions=questions
            )

        values = snapshot.values
        return AgentResponse(
            system_name=values["system_name"],
            risk_tier=values["risk_tier"],
            dpia_required=values["dpia_required"],
            steps_completed=values["steps_completed"],
            final_summary=values["final_summary"],
            dpia_assessment=values.get("dpia_assessment"),
            owasp_assessment=values.get("owasp_assessment")
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/assess/respond", response_model=AgentResponse)
def respond_to_clarification(request: RespondRequest):
    """
    Resume a paused assessment by providing answers to the clarifying questions.
    Use the thread_id returned from the /assess endpoint.
    """
    try:
        config = {"configurable": {"thread_id": request.thread_id}}

        snapshot = compliance_agent.get_state(config)
        if not snapshot or not snapshot.next:
            raise HTTPException(
                status_code=400,
                detail="No paused session found for this thread_id. It may have already completed or expired."
            )

        compliance_agent.invoke(
            Command(resume=request.answers),
            config=config
        )

        final_snapshot = compliance_agent.get_state(config)
        values = final_snapshot.values

        return AgentResponse(
            system_name=values["system_name"],
            risk_tier=values["risk_tier"],
            dpia_required=values["dpia_required"],
            steps_completed=values["steps_completed"],
            final_summary=values["final_summary"],
            dpia_assessment=values.get("dpia_assessment"),
            owasp_assessment=values.get("owasp_assessment")
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))