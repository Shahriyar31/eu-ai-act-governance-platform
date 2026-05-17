from src.models.schemas import ClassificationResponse, OWASPResponse

class NISTAssessment:
    def __init__(self, system_name: str):
        self.system_name = system_name
        self.govern = []
        self.map = []
        self.measure = []
        self.manage = []
        self.overall_maturity = ""
        self.gaps = []

def map_to_nist(
    system_name: str,
    classification: ClassificationResponse,
    owasp: OWASPResponse
) -> NISTAssessment:

    assessment = NISTAssessment(system_name)

    assessment.govern = _assess_govern(classification)
    assessment.map = _assess_map(classification, owasp)
    assessment.measure = _assess_measure(classification, owasp)
    assessment.manage = _assess_manage(classification, owasp)
    assessment.gaps = _identify_gaps(classification, owasp)
    assessment.overall_maturity = _calculate_maturity(classification, owasp)

    return assessment


def _assess_govern(classification: ClassificationResponse) -> list:
    controls = [
        "GOVERN 1.1: Policies and procedures for AI risk management should be established"
    ]

    if classification.risk_tier == "high":
        controls.extend([
            "GOVERN 1.2: Roles and responsibilities for AI oversight must be clearly defined",
            "GOVERN 1.3: AI risk management must be integrated into organisational governance",
            "GOVERN 2.1: Accountability mechanisms for AI decisions must be established",
            "GOVERN 4.1: Organisational teams must be trained on AI risk and responsible AI practices",
            "GOVERN 5.1: Policies for AI transparency and explainability must be documented"
        ])

    if classification.risk_tier == "unacceptable":
        controls.append(
            "GOVERN 6.1: This system falls outside acceptable risk thresholds — deployment must be halted"
        )

    return controls


def _assess_map(
    classification: ClassificationResponse,
    owasp: OWASPResponse
) -> list:

    controls = [
        "MAP 1.1: AI system context and intended use has been documented",
        "MAP 1.5: Organisational risk tolerance for this AI system should be defined"
    ]

    if classification.risk_tier in ["high", "unacceptable"]:
        controls.extend([
            "MAP 2.1: Scientific and domain expertise has been applied to identify AI risks",
            "MAP 2.2: Scientific rigour of AI outputs must be assessed",
            "MAP 3.1: AI system risks to individuals, groups and society must be enumerated",
            "MAP 3.5: Risks to vulnerable populations must be specifically assessed"
        ])

    if len(owasp.risks_found) > 0:
        controls.append(
            f"MAP 4.1: {len(owasp.risks_found)} security risks identified via OWASP LLM Top 10 assessment"
        )

    if classification.dpia_required:
        controls.append(
            "MAP 5.1: Privacy risks have been identified — DPIA required under GDPR Article 35"
        )

    return controls


def _assess_measure(
    classification: ClassificationResponse,
    owasp: OWASPResponse
) -> list:

    controls = [
        "MEASURE 1.1: AI risk measurement approaches appropriate to the system have been identified"
    ]

    if classification.risk_tier == "high":
        controls.extend([
            "MEASURE 2.1: AI system testing must include evaluation of bias and fairness metrics",
            "MEASURE 2.2: Evaluation of AI system explainability must be conducted",
            "MEASURE 2.3: AI system performance must be measured against defined benchmarks",
            "MEASURE 2.6: Robustness and adversarial testing must be performed",
            "MEASURE 2.10: Privacy risk metrics must be tracked and reported"
        ])

    if owasp.severity_level == "critical":
        controls.extend([
            "MEASURE 2.7: Security vulnerabilities have been assessed — critical severity findings require immediate remediation",
            "MEASURE 2.8: Penetration testing is recommended given critical OWASP findings"
        ])
    elif owasp.severity_level == "high":
        controls.append(
            "MEASURE 2.7: Security vulnerabilities assessed — high severity findings require remediation before deployment"
        )

    return controls


def _assess_manage(
    classification: ClassificationResponse,
    owasp: OWASPResponse
) -> list:

    controls = [
        "MANAGE 1.1: Response plans for identified AI risks must be developed and maintained"
    ]

    if classification.risk_tier == "high":
        controls.extend([
            "MANAGE 1.3: Risk response priorities must be established based on likelihood and impact",
            "MANAGE 2.2: Mechanisms to sustain AI system oversight must be implemented",
            "MANAGE 2.4: Incident response procedures for AI-related failures must be documented",
            "MANAGE 3.1: Risks must be tracked and monitored on an ongoing basis",
            "MANAGE 3.2: Residual risks must be documented and accepted by accountable stakeholders",
            "MANAGE 4.1: AI system performance must be monitored post-deployment"
        ])

    if len(owasp.risks_found) > 3:
        controls.append(
            "MANAGE 2.1: Multiple security risks require a prioritised remediation roadmap"
        )

    if classification.dpia_required:
        controls.append(
            "MANAGE 3.3: Data protection risks must be reviewed annually or when system changes occur"
        )

    return controls


def _identify_gaps(
    classification: ClassificationResponse,
    owasp: OWASPResponse
) -> list:

    gaps = []

    if classification.risk_tier == "high" and classification.dpia_required:
        gaps.append("No evidence of completed DPIA — required before deployment")

    if owasp.severity_level in ["critical", "high"]:
        gaps.append(f"Security posture is {owasp.severity_level} — OWASP LLM risks must be addressed")

    if classification.risk_tier == "high":
        gaps.append("EU AI Act registration in EU database required before deployment")
        gaps.append("Human oversight mechanism must be designed and implemented")
        gaps.append("Technical documentation package must be prepared for regulatory review")

    if classification.risk_tier == "unacceptable":
        gaps.append("CRITICAL GAP: System is prohibited — all development must cease immediately")

    return gaps


def _calculate_maturity(
    classification: ClassificationResponse,
    owasp: OWASPResponse
) -> str:

    if classification.risk_tier == "unacceptable":
        return "Not Applicable — Prohibited System"

    if classification.risk_tier == "high" and owasp.severity_level == "critical":
        return "Initial — Significant gaps in AI risk management maturity"

    if classification.risk_tier == "high" and owasp.severity_level == "high":
        return "Developing — Risk management framework partially in place"

    if classification.risk_tier == "high":
        return "Defined — Risk management processes defined but not fully implemented"

    if classification.risk_tier == "limited":
        return "Managed — Risk management processes active with room for improvement"

    return "Optimising — Strong risk management posture for minimal risk system"