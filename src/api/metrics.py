from prometheus_client import Counter

# Custom Business Metrics for EU AI Act Compliance Monitoring

# 1. Total Assessments / Classifications performed
classification_counter = Counter(
    "eu_ai_act_assessments_total",
    "Total number of AI compliance assessments / classifications performed",
    ["risk_tier", "sector"]
)

# 2. Total DPIA Reports generated
dpia_counter = Counter(
    "eu_ai_act_dpia_generated_total",
    "Total number of GDPR DPIA reports generated",
    ["risk_tier"]
)

# 3. Total OWASP LLM Top 10 scans run
owasp_counter = Counter(
    "eu_ai_act_owasp_checks_total",
    "Total number of OWASP LLM security evaluations performed",
    ["uses_llm"]
)

# 4. Total PDF compliance reports generated
pdf_counter = Counter(
    "eu_ai_act_pdf_reports_generated_total",
    "Total compliance assessment PDF reports generated for download",
    ["system_name"]
)
