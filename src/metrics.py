from prometheus_client import Counter

# Incremented every time /classify or /assess-and-download runs
assessments_total = Counter(
    "compliance_assessments_total",
    "Total number of compliance assessments run"
)

# Incremented per assessment, broken down by EU AI Act risk tier
# Label value will be: UNACCEPTABLE, HIGH, LIMITED, or MINIMAL
risk_tier_total = Counter(
    "risk_tier_classifications_total",
    "Compliance assessments broken down by EU AI Act risk tier",
    ["tier"]
)

# Incremented every time a DPIA report is generated
dpia_generated_total = Counter(
    "dpia_generated_total",
    "Total number of DPIA reports generated"
)

# Incremented every time an OWASP LLM check runs
owasp_checks_total = Counter(
    "owasp_checks_total",
    "Total number of OWASP LLM Top 10 checks performed"
)

# Incremented every time a PDF compliance report is generated
pdf_reports_total = Counter(
    "pdf_reports_total",
    "Total number of PDF compliance reports generated"
)