from sqlalchemy.orm import Session
from src.models.schemas import ClassificationRequest, ClassificationResponse, RiskTierEnum, SectorEnum
from src.database.models import ClassificationRule

def classify_ai_system(request: ClassificationRequest, db: Session) -> ClassificationResponse:
    description_lower = request.description.lower()

    rules = db.query(ClassificationRule).filter(
        ClassificationRule.is_active == True
    ).order_by(ClassificationRule.priority.asc()).all()

    for rule in rules:
        if _rule_matches(rule, request, description_lower):
            risk_tier = RiskTierEnum(rule.risk_tier)

            if risk_tier == RiskTierEnum.unacceptable:
                dpia_required = False
            elif risk_tier == RiskTierEnum.minimal:
                dpia_required = False
            else:
                dpia_required = request.processes_personal_data

            justification = rule.justification_template
            if risk_tier == RiskTierEnum.high:
                if request.automated_decision:
                    justification += " Automated decision-making without human review increases risk."
                else:
                    justification += " Human oversight is present which is a positive control."

            obligations = _get_obligations(risk_tier, request)

            return ClassificationResponse(
                system_name=request.system_name,
                risk_tier=risk_tier,
                justification=justification,
                obligations=obligations,
                dpia_required=dpia_required
            )

    return ClassificationResponse(
        system_name=request.system_name,
        risk_tier=RiskTierEnum.minimal,
        justification="System does not fall under any high-risk category defined in EU AI Act Annex III.",
        obligations=["No mandatory EU AI Act obligations apply"],
        dpia_required=False
    )


def _rule_matches(rule: ClassificationRule, request: ClassificationRequest, description_lower: str) -> bool:
    if rule.keyword is not None:
        return rule.keyword in description_lower

    if rule.sector is not None:
        if request.sector.value != rule.sector:
            return False

    if rule.interacts_with_humans is not None:
        if request.interacts_with_humans != rule.interacts_with_humans:
            return False

    if rule.automated_decision is not None:
        if request.automated_decision != rule.automated_decision:
            return False

    if rule.processes_personal_data is not None:
        if request.processes_personal_data != rule.processes_personal_data:
            return False

    return True


def _get_obligations(risk_tier: RiskTierEnum, request: ClassificationRequest) -> list:
    if risk_tier == RiskTierEnum.unacceptable:
        return [
            "This AI system is prohibited under EU AI Act Article 5",
            "Immediate cessation of development and deployment required",
            "Legal review recommended"
        ]

    if risk_tier == RiskTierEnum.limited:
        return [
            "Disclose AI identity to users before interaction begins",
            "Label any AI-generated content clearly",
            "Maintain transparency about system capabilities and limitations"
        ]

    if risk_tier == RiskTierEnum.minimal:
        return [
            "No mandatory EU AI Act obligations apply",
            "Best practice: maintain internal documentation",
            "Best practice: conduct voluntary impact assessments"
        ]

    obligations = [
        "Implement a risk management system (Article 9)",
        "Establish data governance practices (Article 10)",
        "Maintain technical documentation (Article 11)",
        "Enable automatic logging and record-keeping (Article 12)",
        "Ensure transparency for users (Article 13)",
        "Implement human oversight measures (Article 14)",
        "Achieve required accuracy, robustness and cybersecurity (Article 15)",
        "Register system in EU AI Act database before deployment (Article 16)"
    ]

    if request.sector == SectorEnum.healthcare:
        obligations.append("Comply with EU Medical Device Regulation (MDR) if applicable")
        obligations.append("Ensure clinical validation before deployment")

    if request.sector == SectorEnum.employment:
        obligations.append("Inform workers and their representatives about AI use")
        obligations.append("Ensure non-discrimination in automated hiring decisions")

    if request.sector == SectorEnum.law_enforcement:
        obligations.append("Obtain prior judicial or administrative authorisation")
        obligations.append("Maintain detailed logs of every use")

    if request.sector == SectorEnum.border_control:
        obligations.append("Ensure compliance with EU asylum and migration law")
        obligations.append("Prohibit use for decisions affecting right to asylum")

    if request.sector == SectorEnum.education:
        obligations.append("Ensure assessment tools are validated for fairness across student groups")
        obligations.append("Provide human review of AI-generated academic assessments")

    if request.sector == SectorEnum.finance:
        obligations.append("Comply with EU financial services regulations alongside AI Act")
        obligations.append("Ensure explainability of credit or insurance decisions")

    if request.processes_personal_data:
        obligations.append("Conduct Data Protection Impact Assessment (GDPR Article 35)")
        obligations.append("Appoint Data Protection Officer if not already in place")

    if request.automated_decision:
        obligations.append("Implement mandatory human review before decisions take effect")
        obligations.append("Provide mechanism for individuals to contest automated decisions")

    return obligations