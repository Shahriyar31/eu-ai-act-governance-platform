from src.models.schemas import ClassificationRequest, ClassificationResponse, SectorEnum, RiskTierEnum

HIGH_RISK_SECTORS = [
    SectorEnum.healthcare,
    SectorEnum.employment,
    SectorEnum.education,
    SectorEnum.law_enforcement,
    SectorEnum.border_control,
    SectorEnum.critical_infrastructure,
    SectorEnum.justice,
    SectorEnum.finance
]

UNACCEPTABLE_KEYWORDS = [
    "social scoring",
    "mass surveillance",
    "biometric surveillance",
    "subliminal manipulation",
    "exploit vulnerability",
    "real-time biometric"
]

def classify_ai_system(request: ClassificationRequest) -> ClassificationResponse:
    description_lower = request.description.lower()

    for keyword in UNACCEPTABLE_KEYWORDS:
        if keyword in description_lower:
            return ClassificationResponse(
                system_name=request.system_name,
                risk_tier=RiskTierEnum.unacceptable,
                justification=f"System description contains indicators of prohibited AI: '{keyword}'. This system is banned under EU AI Act Article 5.",
                obligations=[
                    "This AI system is prohibited under EU AI Act Article 5",
                    "Immediate cessation of development and deployment required",
                    "Legal review recommended"
                ],
                dpia_required=False
            )

    if request.sector in HIGH_RISK_SECTORS:
        obligations = _get_high_risk_obligations(request)
        return ClassificationResponse(
            system_name=request.system_name,
            risk_tier=RiskTierEnum.high,
            justification=f"System operates in the '{request.sector.value}' sector which is listed under Annex III of the EU AI Act as High Risk. {'Automated decision-making without human review increases risk.' if request.automated_decision else 'Human oversight is present which is a positive control.'}",
            obligations=obligations,
            dpia_required=request.processes_personal_data
        )

    if request.interacts_with_humans:
        return ClassificationResponse(
            system_name=request.system_name,
            risk_tier=RiskTierEnum.limited,
            justification="System interacts directly with humans. Transparency obligations apply under EU AI Act Article 50.",
            obligations=[
                "Disclose AI identity to users before interaction begins",
                "Label any AI-generated content clearly",
                "Maintain transparency about system capabilities and limitations"
            ],
            dpia_required=request.processes_personal_data
        )

    return ClassificationResponse(
        system_name=request.system_name,
        risk_tier=RiskTierEnum.minimal,
        justification="System does not fall under any high-risk category defined in EU AI Act Annex III and does not interact directly with humans in a way that triggers transparency obligations.",
        obligations=[
            "No mandatory EU AI Act obligations apply",
            "Best practice: maintain internal documentation",
            "Best practice: conduct voluntary impact assessments"
        ],
        dpia_required=False
    )


def _get_high_risk_obligations(request: ClassificationRequest) -> list:
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