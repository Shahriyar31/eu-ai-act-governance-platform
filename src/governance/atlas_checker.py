import httpx
import json
from typing import List, Dict

ATLAS_TECHNIQUES_URL = "https://raw.githubusercontent.com/mitre-atlas/atlas-data/main/dist/ATLAS.json"

# Cached ATLAS data — loaded once at startup
_atlas_cache: Dict = {}

class ATLASTechnique:
    def __init__(self, technique_id: str, name: str, description: str, tactics: List[str]):
        self.technique_id = technique_id
        self.name = name
        self.description = description
        self.tactics = tactics

class ATLASAssessment:
    def __init__(self, system_name: str):
        self.system_name = system_name
        self.relevant_techniques = []
        self.tactics_covered = []
        self.risk_summary = ""
        self.recommendations = []

async def load_atlas_data() -> Dict:
    global _atlas_cache

    if _atlas_cache:
        return _atlas_cache

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(ATLAS_TECHNIQUES_URL)
            if response.status_code == 200:
                _atlas_cache = response.json()
                return _atlas_cache
    except Exception:
        pass

    # Fallback to hardcoded key techniques if download fails
    _atlas_cache = _get_fallback_techniques()
    return _atlas_cache


async def assess_atlas_risks(
    system_name: str,
    uses_llm: bool,
    accepts_user_input: bool,
    has_external_api: bool,
    processes_personal_data: bool,
    automated_decision: bool
) -> ATLASAssessment:

    assessment = ATLASAssessment(system_name)
    atlas_data = await load_atlas_data()
    relevant = []

    # Map system characteristics to ATLAS techniques
    if uses_llm and accepts_user_input:
        relevant.extend([
            ATLASTechnique(
                "AML.T0051",
                "LLM Prompt Injection",
                "Adversary crafts malicious inputs to manipulate LLM behaviour and bypass safety controls",
                ["ML Attack Staging"]
            ),
            ATLASTechnique(
                "AML.T0054",
                "LLM Jailbreak",
                "Adversary uses carefully crafted prompts to make LLM ignore its safety guidelines",
                ["ML Attack Staging"]
            )
        ])

    if uses_llm:
        relevant.extend([
            ATLASTechnique(
                "AML.T0043",
                "Craft Adversarial Data",
                "Adversary creates inputs specifically designed to cause incorrect model outputs",
                ["ML Attack Staging"]
            ),
            ATLASTechnique(
                "AML.T0040",
                "ML Model Inference API Access",
                "Adversary repeatedly queries model API to extract information about the model",
                ["Reconnaissance"]
            )
        ])

    if processes_personal_data:
        relevant.extend([
            ATLASTechnique(
                "AML.T0024",
                "Exfiltration via ML Inference API",
                "Adversary extracts training data including personal information through model queries",
                ["Exfiltration"]
            ),
            ATLASTechnique(
                "AML.T0037",
                "Data from Information Repositories",
                "Adversary accesses ML pipeline data stores containing sensitive training data",
                ["Collection"]
            )
        ])

    if automated_decision:
        relevant.extend([
            ATLASTechnique(
                "AML.T0047",
                "ML Artifact Collection",
                "Adversary collects ML artifacts to understand decision boundaries and manipulate outcomes",
                ["Collection"]
            ),
            ATLASTechnique(
                "AML.T0020",
                "Poison Training Data",
                "Adversary introduces malicious data into training pipeline to influence model behaviour",
                ["ML Attack Staging"]
            )
        ])

    if has_external_api:
        relevant.extend([
            ATLASTechnique(
                "AML.T0046",
                "Spear Phishing for ML Access",
                "Adversary targets ML engineers to gain access to models and training pipelines",
                ["Initial Access"]
            ),
            ATLASTechnique(
                "AML.T0053",
                "Denial of ML Service",
                "Adversary overwhelms ML API with requests to degrade service availability",
                ["Impact"]
            )
        ])

    assessment.relevant_techniques = relevant
    assessment.tactics_covered = list(set(
        tactic for technique in relevant for tactic in technique.tactics
    ))
    assessment.risk_summary = _generate_risk_summary(relevant)
    assessment.recommendations = _generate_atlas_recommendations(relevant)

    return assessment


def _generate_risk_summary(techniques: List[ATLASTechnique]) -> str:
    if not techniques:
        return "No specific MITRE ATLAS techniques identified for this system configuration."

    tactic_counts = {}
    for technique in techniques:
        for tactic in technique.tactics:
            tactic_counts[tactic] = tactic_counts.get(tactic, 0) + 1

    most_covered = max(tactic_counts, key=tactic_counts.get) if tactic_counts else "Unknown"

    return (
        f"{len(techniques)} MITRE ATLAS adversarial techniques are relevant to this AI system. "
        f"The highest concentration of techniques falls under '{most_covered}'. "
        f"These techniques represent real-world attack patterns observed against AI systems in production."
    )


def _generate_atlas_recommendations(techniques: List[ATLASTechnique]) -> List[str]:
    recommendations = []
    technique_ids = [t.technique_id for t in techniques]

    if "AML.T0051" in technique_ids or "AML.T0054" in technique_ids:
        recommendations.append(
            "Implement prompt injection defences — validate and sanitise all user inputs before passing to LLM"
        )

    if "AML.T0043" in technique_ids:
        recommendations.append(
            "Deploy adversarial robustness testing — evaluate model behaviour against crafted adversarial inputs"
        )

    if "AML.T0040" in technique_ids:
        recommendations.append(
            "Implement API rate limiting and monitoring to detect model extraction attempts"
        )

    if "AML.T0024" in technique_ids or "AML.T0037" in technique_ids:
        recommendations.append(
            "Apply differential privacy techniques to prevent training data extraction via inference"
        )

    if "AML.T0020" in technique_ids:
        recommendations.append(
            "Validate training data integrity — implement checksums and provenance tracking for all training datasets"
        )

    if "AML.T0053" in technique_ids:
        recommendations.append(
            "Implement DoS protection — rate limiting, request queuing, and circuit breakers for ML APIs"
        )

    recommendations.extend([
        "Review MITRE ATLAS case studies relevant to your sector at https://atlas.mitre.org",
        "Conduct adversarial ML testing as part of your pre-deployment security assessment",
        "Subscribe to MITRE ATLAS updates as new AI attack techniques are documented"
    ])

    return recommendations


def _get_fallback_techniques() -> Dict:
    # Minimal fallback if ATLAS download fails
    return {
        "techniques": [],
        "source": "fallback"
    }