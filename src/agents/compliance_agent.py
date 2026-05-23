"""
LangGraph Compliance Workflow Agent with Human-in-the-Loop.

Graph structure:
    START → classify → [router] → clarification (interrupt) → dpia → owasp → summary → END
                               ↘ summary → END (minimal/unacceptable)
"""

from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt
from src.database.connection import SessionLocal
from src.models.schemas import (
    ClassificationRequest, DPIARequest, OWASPRequest,
    SectorEnum, RiskTierEnum
)
from src.governance.classifier import classify_ai_system
from src.governance.dpia import generate_dpia
from src.governance.owasp import check_owasp_llm
from langchain_core.messages import HumanMessage
from src.ai.llm_factory import get_agent_llm, ModelLogger


class ComplianceState(TypedDict):
    system_name: str
    description: str
    sector: str
    automated_decision: bool
    processes_personal_data: bool
    interacts_with_humans: bool
    uses_llm: bool
    accepts_user_input: bool

    risk_tier: str
    dpia_required: bool
    classification_justification: str
    classification_obligations: list

    clarification_questions: list
    user_clarifications: Optional[str]

    dpia_assessment: Optional[dict]
    owasp_assessment: Optional[dict]

    final_summary: str
    steps_completed: list


def _generate_clarification_questions(state: ComplianceState) -> list[str]:
    risk_tier = state["risk_tier"]
    sector = state["sector"]
    questions = []

    if risk_tier == "high":
        questions.append(
            "Does this system make final decisions automatically with no human reviewing "
            "each case, or does a human always review the AI recommendation before it takes effect?"
        )

    if sector == "employment":
        questions.append(
            "Will candidates be informed that AI is used to screen or rank them, "
            "and will they have a right to request human review?"
        )
    elif sector == "healthcare":
        questions.append(
            "Does this system directly influence clinical decisions such as diagnosis, "
            "treatment selection, or medication dosing?"
        )
    elif sector == "education":
        questions.append(
            "Does this system make or influence decisions about student admission, "
            "assessment scores, or academic progression?"
        )
    elif sector == "finance":
        questions.append(
            "Does this system make credit scoring, loan approval, or insurance risk "
            "decisions that directly affect individuals?"
        )
    else:
        questions.append(
            "Will this system affect individuals in ways they cannot easily contest "
            "or appeal, and are those individuals aware the system exists?"
        )

    if state["processes_personal_data"]:
        questions.append(
            "What categories of personal data does this system process? "
            "For example: names and emails only, or sensitive data such as "
            "health records, ethnicity, biometrics, or financial history?"
        )

    return questions[:3]


def classify_node(state: ComplianceState) -> dict:
    db = SessionLocal()
    try:
        request = ClassificationRequest(
            system_name=state["system_name"],
            description=state["description"],
            sector=SectorEnum(state["sector"]),
            automated_decision=state["automated_decision"],
            processes_personal_data=state["processes_personal_data"],
            interacts_with_humans=state["interacts_with_humans"]
        )
        result = classify_ai_system(request, db)
        return {
            "risk_tier": result.risk_tier.value,
            "dpia_required": result.dpia_required,
            "classification_justification": result.justification,
            "classification_obligations": result.obligations,
            "steps_completed": ["classification"]
        }
    finally:
        db.close()


def clarification_node(state: ComplianceState) -> dict:
    """
    Pause point. Generates questions based on what classification found,
    then calls interrupt() to wait for the user's answers.
    After the user responds, interrupt() returns their answers and
    the graph continues to dpia_node.
    """
    questions = _generate_clarification_questions(state)

    # interrupt() saves the entire graph state to the checkpointer,
    # then pauses. The value passed in (questions) is stored as
    # interrupt metadata — readable from outside the graph.
    # When the user sends answers, interrupt() returns those answers.
    user_answer = interrupt(questions)

    return {
        "clarification_questions": questions,
        "user_clarifications": str(user_answer),
        "steps_completed": state["steps_completed"] + ["clarification"]
    }


def dpia_node(state: ComplianceState) -> dict:
    request = DPIARequest(
        system_name=state["system_name"],
        description=state["description"],
        sector=SectorEnum(state["sector"]),
        data_subjects="Users and individuals processed by the system",
        data_types="Personal data as described in the system description",
        processing_purpose="As described in the system description",
        risk_tier=RiskTierEnum(state["risk_tier"])
    )
    result = generate_dpia(request)
    return {
        "dpia_assessment": {
            "required": result.dpia_required,
            "summary": result.assessment_summary,
            "risks": result.risks_identified,
            "mitigations": result.mitigation_measures,
            "recommendation": result.recommendation
        },
        "steps_completed": state["steps_completed"] + ["dpia"]
    }


def owasp_node(state: ComplianceState) -> dict:
    request = OWASPRequest(
        system_name=state["system_name"],
        description=state["description"],
        uses_llm=state["uses_llm"],
        accepts_user_input=state["accepts_user_input"],
        produces_output_used_in_decisions=state["automated_decision"],
        has_access_to_external_systems=False
    )
    result = check_owasp_llm(request)
    return {
        "owasp_assessment": {
            "risks_found": result.risks_found,
            "severity": result.severity_level,
            "recommendations": result.recommendations
        },
        "steps_completed": state["steps_completed"] + ["owasp"]
    }


def summary_node(state: ComplianceState) -> dict:
    risk_tier = state["risk_tier"]

    clarification_section = ""
    if state.get("user_clarifications"):
        clarification_section = f"""
CLARIFICATIONS PROVIDED BY THE ORGANISATION:
Questions asked: {state.get('clarification_questions', [])}
Answers received: {state['user_clarifications']}

Use these answers to make the report more specific and accurate.
"""

    dpia_section = ""
    if state.get("dpia_assessment"):
        dpia = state["dpia_assessment"]
        dpia_section = f"""
GDPR DPIA FINDINGS:
Summary: {dpia['summary']}
Risks identified: {', '.join(dpia['risks'])}
Mitigations: {', '.join(dpia['mitigations'])}
Recommendation: {dpia['recommendation']}
"""

    owasp_section = ""
    if state.get("owasp_assessment"):
        owasp = state["owasp_assessment"]
        owasp_section = f"""
OWASP LLM SECURITY FINDINGS:
Severity: {owasp['severity']}
Risks found: {', '.join(owasp['risks_found'])}
Recommendations: {', '.join(owasp['recommendations'][:3])}
"""

    prohibited_note = ""
    if risk_tier == "unacceptable":
        prohibited_note = (
            "IMPORTANT: This system is PROHIBITED under EU AI Act Article 5. "
            "State this clearly and urgently at the start of the report."
        )

    prompt = f"""You are a senior EU AI Act compliance officer writing a formal compliance assessment report.

Write a structured, professional compliance report based on the findings below.
Use clear headings. Be specific about obligations, timelines, and regulatory references.
Write for a technical and legal audience. Every sentence must add value.

SYSTEM UNDER ASSESSMENT: {state['system_name']}
DESCRIPTION: {state['description']}
SECTOR: {state['sector']}
EU AI ACT RISK TIER: {risk_tier.upper()}

CLASSIFICATION JUSTIFICATION:
{state['classification_justification']}

KEY OBLIGATIONS IDENTIFIED:
{chr(10).join(f'- {o}' for o in state.get('classification_obligations', []))}
{clarification_section}
{dpia_section}
{owasp_section}
{prohibited_note}

Write the full compliance assessment report now:"""

    try:
        llm = get_agent_llm()
        response = llm.invoke(
            [HumanMessage(content=prompt)],
            config={"callbacks": [ModelLogger("[Agent]")]}
        )
        summary = response.content

    except Exception as e:
        print(f"[Agent] LLM summary failed, using structured fallback: {e}")
        parts = [
            f"## Compliance Assessment: {state['system_name']}",
            f"**Risk Tier:** {risk_tier.upper()}",
            f"**Justification:** {state['classification_justification']}",
        ]
        for obligation in state.get("classification_obligations", [])[:5]:
            parts.append(f"- {obligation}")
        summary = "\n".join(parts)

    steps = state.get("steps_completed", [])
    return {
        "final_summary": summary,
        "steps_completed": steps + ["summary"]
    }


def route_after_classification(state: ComplianceState) -> str:
    risk_tier = state["risk_tier"]
    if risk_tier in ["high", "limited"]:
        return "ask_clarification"
    else:
        return "skip_to_summary"


def build_compliance_agent():
    graph = StateGraph(ComplianceState)

    graph.add_node("classify", classify_node)
    graph.add_node("clarification", clarification_node)
    graph.add_node("dpia", dpia_node)
    graph.add_node("owasp", owasp_node)
    graph.add_node("summary", summary_node)

    graph.set_entry_point("classify")

    graph.add_conditional_edges(
        "classify",
        route_after_classification,
        {
            "ask_clarification": "clarification",
            "skip_to_summary": "summary"
        }
    )

    graph.add_edge("clarification", "dpia")
    graph.add_edge("dpia", "owasp")
    graph.add_edge("owasp", "summary")
    graph.add_edge("summary", END)

    checkpointer = MemorySaver()
    return graph.compile(checkpointer=checkpointer)


compliance_agent = build_compliance_agent()