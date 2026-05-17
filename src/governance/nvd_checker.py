import httpx
from typing import List, Dict
from datetime import datetime

NVD_API_BASE = "https://services.nvd.nist.gov/rest/json/cves/2.0"

class CVEFinding:
    def __init__(self, cve_id: str, description: str, severity: str, score: float, published: str):
        self.cve_id = cve_id
        self.description = description
        self.severity = severity
        self.score = score
        self.published = published

class NVDAssessment:
    def __init__(self, system_name: str):
        self.system_name = system_name
        self.technologies_checked = []
        self.findings = []
        self.critical_count = 0
        self.high_count = 0
        self.medium_count = 0
        self.overall_risk = ""
        self.recommendations = []

async def check_technologies_nvd(
    system_name: str,
    technologies: List[str]
) -> NVDAssessment:

    assessment = NVDAssessment(system_name)
    assessment.technologies_checked = technologies

    async with httpx.AsyncClient(timeout=30.0) as client:
        for technology in technologies:
            findings = await _query_nvd(client, technology)
            assessment.findings.extend(findings)

            for finding in findings:
                if finding.severity == "CRITICAL":
                    assessment.critical_count += 1
                elif finding.severity == "HIGH":
                    assessment.high_count += 1
                elif finding.severity == "MEDIUM":
                    assessment.medium_count += 1

    assessment.overall_risk = _calculate_overall_risk(assessment)
    assessment.recommendations = _generate_recommendations(assessment)

    return assessment


async def _query_nvd(client: httpx.AsyncClient, technology: str) -> List[CVEFinding]:
    findings = []

    try:
        response = await client.get(
            NVD_API_BASE,
            params={
                "keywordSearch": technology,
                "resultsPerPage": 10,
                "cvssV3Severity": "CRITICAL"
            }
        )

        if response.status_code != 200:
            return findings

        data = response.json()
        vulnerabilities = data.get("vulnerabilities", [])

        for vuln in vulnerabilities:
            cve = vuln.get("cve", {})
            cve_id = cve.get("id", "Unknown")

            descriptions = cve.get("descriptions", [])
            description = next(
                (d["value"] for d in descriptions if d["lang"] == "en"),
                "No description available"
            )

            metrics = cve.get("metrics", {})
            severity = "UNKNOWN"
            score = 0.0

            if "cvssMetricV31" in metrics:
                cvss_data = metrics["cvssMetricV31"][0]["cvssData"]
                severity = cvss_data.get("baseSeverity", "UNKNOWN")
                score = cvss_data.get("baseScore", 0.0)
            elif "cvssMetricV30" in metrics:
                cvss_data = metrics["cvssMetricV30"][0]["cvssData"]
                severity = cvss_data.get("baseSeverity", "UNKNOWN")
                score = cvss_data.get("baseScore", 0.0)

            published = cve.get("published", "Unknown")

            findings.append(CVEFinding(
                cve_id=cve_id,
                description=description[:200],
                severity=severity,
                score=score,
                published=published
            ))

    except httpx.TimeoutException:
        findings.append(CVEFinding(
            cve_id="TIMEOUT",
            description=f"NVD query timed out for {technology}",
            severity="UNKNOWN",
            score=0.0,
            published="N/A"
        ))
    except Exception as e:
        findings.append(CVEFinding(
            cve_id="ERROR",
            description=f"Could not query NVD for {technology}: {str(e)}",
            severity="UNKNOWN",
            score=0.0,
            published="N/A"
        ))

    return findings


def _calculate_overall_risk(assessment: NVDAssessment) -> str:
    if assessment.critical_count > 0:
        return f"CRITICAL — {assessment.critical_count} critical CVEs found across assessed technologies"
    elif assessment.high_count > 0:
        return f"HIGH — {assessment.high_count} high severity CVEs found"
    elif assessment.medium_count > 0:
        return f"MEDIUM — {assessment.medium_count} medium severity CVEs found"
    else:
        return "LOW — No critical or high severity CVEs found in assessed technologies"


def _generate_recommendations(assessment: NVDAssessment) -> List[str]:
    recommendations = []

    if assessment.critical_count > 0:
        recommendations.append(
            f"IMMEDIATE ACTION: {assessment.critical_count} critical CVEs identified. "
            "Upgrade affected components before deployment."
        )

    if assessment.high_count > 0:
        recommendations.append(
            f"HIGH PRIORITY: {assessment.high_count} high severity CVEs identified. "
            "Schedule upgrades within 30 days."
        )

    recommendations.extend([
        "Subscribe to NVD notifications for all production technologies",
        "Implement automated dependency scanning in your CI/CD pipeline",
        "Establish a vulnerability management policy with defined SLAs for remediation",
        "Review CVE findings against your specific deployment context — not all CVEs are exploitable in every environment"
    ])

    return recommendations