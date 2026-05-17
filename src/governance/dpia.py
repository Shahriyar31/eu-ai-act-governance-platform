from src.models.schemas import DPIARequest, DPIAResponse

def generate_dpia(request: DPIARequest) -> DPIAResponse:

    # Determine if DPIA is actually required
    dpia_required = _is_dpia_required(request)

    if not dpia_required:
        return DPIAResponse(
            system_name=request.system_name,
            dpia_required=False,
            assessment_summary=f"A DPIA is not mandatory for {request.system_name} based on the provided information. The system does not meet the threshold for high-risk processing under GDPR Article 35.",
            risks_identified=[],
            mitigation_measures=[],
            recommendation="No DPIA required. Maintain internal records of this assessment decision."
        )

    risks = _identify_risks(request)
    mitigations = _identify_mitigations(request, risks)
    summary = _generate_summary(request, risks)
    recommendation = _generate_recommendation(request, risks)

    return DPIAResponse(
        system_name=request.system_name,
        dpia_required=True,
        assessment_summary=summary,
        risks_identified=risks,
        mitigation_measures=mitigations,
        recommendation=recommendation
    )


def _is_dpia_required(request: DPIARequest) -> bool:
    # DPIA required for High Risk AI systems processing personal data
    high_risk_tiers = ["high", "unacceptable"]
    if request.risk_tier.lower() in high_risk_tiers:
        return True

    # DPIA required for sensitive data categories under GDPR Article 9
    sensitive_data_keywords = [
        "health", "medical", "biometric", "genetic",
        "racial", "ethnic", "political", "religious",
        "sexual", "criminal"
    ]
    data_types_lower = request.data_types.lower()
    for keyword in sensitive_data_keywords:
        if keyword in data_types_lower:
            return True

    return False


def _identify_risks(request: DPIARequest) -> list:
    risks = []

    # Sector-specific risks
    sector_risks = {
        "healthcare": [
            "Incorrect diagnosis or treatment recommendation causing patient harm",
            "Unauthorised access to sensitive medical records",
            "Algorithmic bias leading to unequal treatment across patient demographics"
        ],
        "employment": [
            "Discriminatory automated decisions affecting employment opportunities",
            "Unlawful processing of candidate personal data without valid legal basis",
            "Lack of transparency denying candidates right to explanation"
        ],
        "education": [
            "Inaccurate assessment causing unfair academic outcomes",
            "Profiling of students based on sensitive characteristics",
            "Data retention beyond necessary period"
        ],
        "law_enforcement": [
            "False positive identifications leading to wrongful investigation",
            "Disproportionate surveillance of individuals",
            "Algorithmic bias resulting in discriminatory enforcement"
        ],
        "finance": [
            "Discriminatory credit or insurance decisions",
            "Opaque automated decisions denying individuals financial services",
            "Data breaches exposing sensitive financial information"
        ]
    }

    sector = request.sector.value
    if sector in sector_risks:
        risks.extend(sector_risks[sector])

    # General risks based on data types
    if "biometric" in request.data_types.lower():
        risks.append("Irreversible harm from biometric data breach — unlike passwords, biometrics cannot be changed")

    if "health" in request.data_types.lower() or "medical" in request.data_types.lower():
        risks.append("Sensitive health data exposure causing reputational, financial or physical harm to data subjects")

    # Risk from automated decision making
    if "automat" in request.processing_purpose.lower():
        risks.append("Automated decisions made without meaningful human review violating GDPR Article 22")

    # General risks always present
    risks.extend([
        "Data breach exposing personal information of data subjects",
        "Processing beyond stated purpose violating purpose limitation principle",
        "Retention of data beyond necessary period violating storage limitation principle"
    ])

    return risks


def _identify_mitigations(request: DPIARequest, risks: list) -> list:
    mitigations = [
        "Implement data minimisation — collect only data strictly necessary for the stated purpose",
        "Apply pseudonymisation or anonymisation where technically feasible",
        "Establish access controls ensuring only authorised personnel access personal data",
        "Implement encryption of personal data at rest and in transit",
        "Define and enforce strict data retention periods with automated deletion",
        "Establish a process for data subjects to exercise their GDPR rights — access, rectification, erasure",
        "Conduct regular audits of data processing activities",
        "Train all staff with access to personal data on GDPR obligations"
    ]

    # Sector-specific mitigations
    if request.sector.lower() == "employment":
        mitigations.append("Inform candidates that automated tools are used in the hiring process")
        mitigations.append("Provide candidates with right to human review of automated decisions")

    if request.sector.lower() == "healthcare":
        mitigations.append("Ensure clinical validation of AI outputs before use in patient care")
        mitigations.append("Maintain audit trail of all AI-assisted clinical decisions")

    if request.sector.lower() == "law_enforcement":
        mitigations.append("Require judicial authorisation before using AI outputs to affect individual rights")
        mitigations.append("Implement mandatory human review of all AI-generated risk assessments")

    # Mitigations for sensitive data
    if "biometric" in request.data_types.lower():
        mitigations.append("Store biometric data in separate encrypted database with restricted access")
        mitigations.append("Obtain explicit consent from data subjects for biometric processing")

    return mitigations


def _generate_summary(request: DPIARequest, risks: list) -> str:
    return (
        f"This DPIA covers the processing of personal data by '{request.system_name}' "
        f"operating in the {request.sector} sector. "
        f"The system processes {request.data_types} belonging to {request.data_subjects} "
        f"for the purpose of {request.processing_purpose}. "
        f"Based on the EU AI Act risk classification of '{request.risk_tier}' and the nature "
        f"of data processed, a DPIA is mandatory under GDPR Article 35. "
        f"This assessment has identified {len(risks)} risks requiring mitigation measures."
    )


def _generate_recommendation(request: DPIARequest, risks: list) -> str:
    if len(risks) > 6:
        return (
            "HIGH PRIORITY: Multiple significant risks identified. Do not deploy this system "
            "until all mitigation measures are implemented and independently reviewed. "
            "Consult your Data Protection Officer and consider consulting the supervisory "
            "authority before deployment."
        )
    elif len(risks) > 3:
        return (
            "MEDIUM PRIORITY: Several risks identified. Implement all mitigation measures "
            "before deployment. Document the implementation and have your Data Protection "
            "Officer review and sign off on this assessment."
        )
    else:
        return (
            "LOW PRIORITY: Risks are manageable. Implement mitigation measures, "
            "document this assessment, and review annually or when the system changes significantly."
        )