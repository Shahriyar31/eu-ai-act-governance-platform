"""
LangGraph Compliance Workflow Agent.

Takes an AI system description and automatically runs the full
compliance pipeline — classification, DPIA, OWASP — making decisions
about which steps to run based on the risk tier found.

Graph structure:
    START → classify → [router] → dpia → owasp → summary → END
                               ↘ summary → END (minimal/unacceptable)
"""

from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from src.database.connection import SessionLocal
from src.models.schemas import (
    ClassificationRequest, DPIARequest, OWASPRequest,
    SectorEnum, RiskTierEnum
)
from src.governance.classifier import classify_ai_system
from src.governance.dpia import generate_dpia
from src.governance.owasp import check_owasp_llm


class ComplianceState(TypedDict):
    """
    The shared notepad passed between every node in the graph.
    Each node reads what it needs and writes its results back.
    """
    # inputs — set at the start, never change
    system_name: str
    description: str
    sector: str
    automated_decision: bool
    processes_personal_data: bool
    interacts_with_humans: bool
    uses_llm: bool
    accepts_user_input: bool

    # outputs — filled in as nodes run
    risk_tier: str
    dpia_required: bool
    classification_justification: str
    classification_obligations: list

    # optional — only filled if the router decides to run them
    dpia_assessment: Optional[dict]
    owasp_assessment: Optional[dict]

    # final output
    final_summary: str
    steps_completed: list


def classify_node(state: ComplianceState) -> dict:
    """
    Node 1: Classify the AI system's EU AI Act risk tier.
    Reads from DB rules, returns risk tier and obligations.
    """
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


def dpia_node(state: ComplianceState) -> dict:
    """
    Node 2: Generate a GDPR Data Protection Impact Assessment.
    Only runs for HIGH and LIMITED risk systems.
    """
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
    """
    Node 3: Run OWASP LLM Top 10 security assessment.
    Runs after DPIA for high/limited risk systems.
    """
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
    """
    Final node: compile all results into a structured summary.
    Runs regardless of which path was taken through the graph.
    """
    risk_tier = state["risk_tier"]

    parts = [
        f"## Compliance Assessment: {state['system_name']}",
        "",
        "### Risk Classification",
        f"**Risk Tier:** {risk_tier.upper()}",
        f"**Justification:** {state['classification_justification']}",
        "",
        "### Key Obligations",
    ]

    for obligation in state.get("classification_obligations", [])[:5]:
        parts.append(f"- {obligation}")

    if state.get("dpia_assessment"):
        dpia = state["dpia_assessment"]
        parts.extend([
            "",
            "### GDPR Data Protection Impact Assessment",
            dpia["summary"],
            f"**Recommendation:** {dpia['recommendation']}"
        ])

    if state.get("owasp_assessment"):
        owasp = state["owasp_assessment"]
        parts.extend([
            "",
            "### OWASP LLM Security Assessment",
            f"**Severity:** {owasp['severity']}",
            f"**Key Risks Identified:** {', '.join(owasp['risks_found'][:3])}"
        ])

    if risk_tier == "unacceptable":
        parts.extend([
            "",
            "### ⚠️ Prohibited System",
            "This AI system is prohibited under EU AI Act Article 5.",
            "Development and deployment must cease immediately.",
            "Legal review is strongly recommended."
        ])

    steps = state.get("steps_completed", [])
    parts.extend([
        "",
        f"### Workflow Summary",
        f"Steps completed automatically: {' → '.join(steps)}"
    ])

    return {
        "final_summary": "\n".join(parts),
        "steps_completed": steps + ["summary"]
    }


def route_after_classification(state: ComplianceState) -> str:
    """
    The decision point — called after classify_node.
    Returns the name of the next node to run.

    This is what makes this an agent rather than a simple pipeline.
    The path through the graph changes based on the classification result.
    """
    risk_tier = state["risk_tier"]

    if risk_tier in ["high", "limited"]:
        # full assessment: dpia → owasp → summary
        return "run_full_assessment"
    else:
        # minimal or unacceptable: skip straight to summary
        return "skip_to_summary"


def build_compliance_agent():
    """Construct and compile the LangGraph workflow."""
    graph = StateGraph(ComplianceState)

    # register all nodes
    graph.add_node("classify", classify_node)
    graph.add_node("dpia", dpia_node)
    graph.add_node("owasp", owasp_node)
    graph.add_node("summary", summary_node)

    # classify is always first
    graph.set_entry_point("classify")

    # after classify: conditional routing based on risk tier
    graph.add_conditional_edges(
        "classify",
        route_after_classification,
        {
            "run_full_assessment": "dpia",
            "skip_to_summary": "summary"
        }
    )

    # dpia always leads to owasp
    graph.add_edge("dpia", "owasp")

    # owasp always leads to summary
    graph.add_edge("owasp", "summary")

    # summary is the terminal node
    graph.add_edge("summary", END)

    return graph.compile()


# compile once at module level — reused across all requests
compliance_agent = build_compliance_agent()