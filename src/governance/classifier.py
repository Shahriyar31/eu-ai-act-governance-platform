from src.models.schemas import ClassificationRequest, ClassificationResponse

# Annex III High Risk sectors from EU AI Act
HIGH_RISK_SECTORS = [
    "healthcare",
    "employment",
    "education",
    "law_enforcement",
    "border_control",
    "critical_infrastructure",
    "justice",
    "finance"
]

# Keywords that indicate Unacceptable Risk
UNACCEPTABLE_KEYWORDS = [
    "social scoring",
    "mass surveillance",
    "biometric surveillance",
    "subliminal manipulation",
    "exploit vulnerability",
    "real-time biometric"
]

def classify_ai_system(request: ClassificationRequest) -> ClassificationResponse:
    # Check Unacceptable Risk first
    description_lower = request.description.lower()

    for keyword in UNACCEPTABLE_KEYWORDS:
        if keyword in description_lower:
            return ClassificationResponse(
                system_name=request.system_name,
                risk_tier="unacceptable",
                justification=f"System description contains indicators of prohibited AI: '{keyword}'. This system is banned under EU AI Act Article 5.",
                obligations=[
                    "This AI system is prohibited under EU AI Act Article 5",
                    "Immediate cessation of development and deployment required",
                    "Legal review recommended"
                ],
                dpia_required=False
            )

    # Check High Risk
    if request.sector.lower() in HIGH_RISK_SECTORS:
        obligations = _get_high_risk_obligations(request)
        return ClassificationResponse(
            system_name=request.system_name,
            risk_tier="high",
            justification=f"System operates in the '{request.sector}' sector which is listed under Annex III of the EU AI Act as High Risk. {'Automated decision-making without human review increases risk.' if request.automated_decision else 'Human oversight is present which is a positive control.'}",
            obligations=obligations,
            dpia_required=request.processes_personal_data
        )

    # Check Limited Risk
    if request.interacts_with_humans:
        return ClassificationResponse(
            system_name=request.system_name,
            risk_tier="limited",
            justification="System interacts directly with humans. Transparency obligations apply under EU AI Act Article 50. Users must be informed they are interacting with an AI system.",
            obligations=[
                "Disclose AI identity to users before interaction begins",
                "Label any AI-generated content clearly",
                "Maintain transparency about system capabilities and limitations"
            ],
            dpia_required=request.processes_personal_data
        )

    # Default — Minimal Risk
    return ClassificationResponse(
        system_name=request.system_name,
        risk_tier="minimal",
        justification="System does not fall under any high-risk category defined in EU AI Act Annex III and does not interact directly with humans in a way that triggers transparency obligations.",
        obligations=[
            "No mandatory EU AI Act obligations apply",
            "Best practice: maintain internal documentation",
            "Best practice: conduct voluntary impact assessments"
        ],
        dpia_required=False
    )


def _get_high_risk_obligations(request: ClassificationRequest) -> list:
    # Base obligations for all High Risk systems
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

    # Add sector-specific obligations
    if request.sector.lower() == "healthcare":
        obligations.append("Comply with EU Medical Device Regulation (MDR) if applicable")
        obligations.append("Ensure clinical validation before deployment")

    if request.sector.lower() == "employment":
        obligations.append("Inform workers and their representatives about AI use")
        obligations.append("Ensure non-discrimination in automated hiring decisions")

    if request.sector.lower() == "law_enforcement":
        obligations.append("Obtain prior judicial or administrative authorisation")
        obligations.append("Maintain detailed logs of every use")

    # Add DPIA obligation if personal data is processed
    if request.processes_personal_data:
        obligations.append("Conduct Data Protection Impact Assessment (GDPR Article 35)")
        obligations.append("Appoint Data Protection Officer if not already in place")

    # Add obligation if no human oversight
    if request.automated_decision:
        obligations.append("Implement mandatory human review before decisions take effect")
        obligations.append("Provide mechanism for individuals to contest automated decisions")

    return obligations