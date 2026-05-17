from src.models.schemas import OWASPRequest, OWASPResponse

# OWASP LLM Top 10 2025 definitions
OWASP_LLM_RISKS = {
    "LLM01": {
        "name": "Prompt Injection",
        "description": "Attackers manipulate LLM behaviour through crafted inputs, bypassing safety controls",
        "condition": lambda req: req.accepts_user_input,
        "severity": "critical"
    },
    "LLM02": {
        "name": "Sensitive Information Disclosure",
        "description": "LLM reveals confidential data from training data or context window",
        "condition": lambda req: req.uses_llm,
        "severity": "high"
    },
    "LLM03": {
        "name": "Supply Chain Vulnerabilities",
        "description": "Risks from third-party models, datasets, or plugins used in the system",
        "condition": lambda req: req.uses_llm,
        "severity": "high"
    },
    "LLM04": {
        "name": "Data and Model Poisoning",
        "description": "Manipulation of training data or fine-tuning process to introduce backdoors",
        "condition": lambda req: req.uses_llm,
        "severity": "high"
    },
    "LLM05": {
        "name": "Improper Output Handling",
        "description": "LLM output passed to downstream systems without validation or sanitisation",
        "condition": lambda req: req.produces_output_used_in_decisions,
        "severity": "critical"
    },
    "LLM06": {
        "name": "Excessive Agency",
        "description": "LLM granted excessive permissions or autonomy to take real-world actions",
        "condition": lambda req: req.has_access_to_external_systems,
        "severity": "critical"
    },
    "LLM07": {
        "name": "System Prompt Leakage",
        "description": "System prompts containing sensitive instructions exposed to users",
        "condition": lambda req: req.accepts_user_input and req.uses_llm,
        "severity": "medium"
    },
    "LLM08": {
        "name": "Vector and Embedding Weaknesses",
        "description": "Vulnerabilities in vector databases or embedding models used for RAG",
        "condition": lambda req: req.has_access_to_external_systems and req.uses_llm,
        "severity": "medium"
    },
    "LLM09": {
        "name": "Misinformation",
        "description": "LLM generates plausible but incorrect information used in high-stakes decisions",
        "condition": lambda req: req.produces_output_used_in_decisions,
        "severity": "high"
    },
    "LLM10": {
        "name": "Unbounded Consumption",
        "description": "Excessive resource consumption through model abuse or denial of service attacks",
        "condition": lambda req: req.accepts_user_input,
        "severity": "medium"
    }
}

# Recommendations for each risk
OWASP_RECOMMENDATIONS = {
    "LLM01": "Implement input validation and prompt sanitisation. Use separate LLM instances for user input and system logic. Apply least-privilege principle to LLM instructions.",
    "LLM02": "Avoid including sensitive data in prompts. Implement output filtering. Apply data classification before including in context window.",
    "LLM03": "Vet all third-party models and plugins. Pin model versions. Monitor for supply chain advisories.",
    "LLM04": "Validate training datasets. Monitor model behaviour for unexpected changes. Use differential privacy where possible.",
    "LLM05": "Treat all LLM output as untrusted. Validate and sanitise before passing to downstream systems. Never execute LLM output directly.",
    "LLM06": "Apply least-privilege to all LLM tool access. Require human approval for consequential actions. Log all external system interactions.",
    "LLM07": "Do not include secrets in system prompts. Assume system prompts are accessible to determined users. Use separate credential management.",
    "LLM08": "Validate and sanitise all data before embedding. Implement access controls on vector databases. Monitor for unusual query patterns.",
    "LLM09": "Implement human review for high-stakes decisions. Add confidence scoring to outputs. Display uncertainty to end users.",
    "LLM10": "Implement rate limiting and request quotas. Monitor resource consumption. Set maximum token limits per request."
}

SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def check_owasp_llm(request: OWASPRequest) -> OWASPResponse:
    risks_found = []
    recommendations = []
    severities = []

    for risk_id, risk_data in OWASP_LLM_RISKS.items():
        # Check if this risk applies to this system
        if risk_data["condition"](request):
            risk_description = f"{risk_id} - {risk_data['name']} ({risk_data['severity'].upper()}): {risk_data['description']}"
            risks_found.append(risk_description)
            recommendations.append(f"{risk_id}: {OWASP_RECOMMENDATIONS[risk_id]}")
            severities.append(risk_data["severity"])

    # Determine overall severity
    overall_severity = _calculate_overall_severity(severities)

    return OWASPResponse(
        system_name=request.system_name,
        risks_found=risks_found,
        severity_level=overall_severity,
        recommendations=recommendations
    )


def _calculate_overall_severity(severities: list) -> str:
    if not severities:
        return "none"

    # Return the most severe level found
    sorted_severities = sorted(severities, key=lambda s: SEVERITY_ORDER.get(s, 99))
    return sorted_severities[0]