from pydantic import BaseModel, Field
from typing import List, Optional

# Request model — what the user sends to the classifier
class ClassificationRequest(BaseModel):
    system_name: str = Field(..., description="Name of the AI system being assessed")
    description: str = Field(..., description="What the AI system does")
    sector: str = Field(..., description="Sector: healthcare, employment, education, finance, law_enforcement, other")
    automated_decision: bool = Field(..., description="Makes decisions without human review")
    processes_personal_data: bool = Field(..., description="Processes personal data of individuals")
    interacts_with_humans: bool = Field(..., description="Directly interacts with humans")

# Response model — what the classifier returns
class ClassificationResponse(BaseModel):
    system_name: str
    risk_tier: str
    justification: str
    obligations: List[str]
    dpia_required: bool

# Request model for DPIA generation
class DPIARequest(BaseModel):
    system_name: str
    description: str
    sector: str
    data_subjects: str = Field(..., description="Who the personal data belongs to — employees, patients, customers")
    data_types: str = Field(..., description="What personal data is processed — names, health data, financial data")
    processing_purpose: str = Field(..., description="Why the data is being processed")
    risk_tier: str = Field(..., description="Risk tier from classification — high, limited, minimal")

# Response model for DPIA
class DPIAResponse(BaseModel):
    system_name: str
    dpia_required: bool
    assessment_summary: str
    risks_identified: List[str]
    mitigation_measures: List[str]
    recommendation: str

# Request model for OWASP LLM Top 10 check
class OWASPRequest(BaseModel):
    system_name: str
    description: str
    uses_llm: bool = Field(..., description="Whether the system uses a large language model")
    accepts_user_input: bool = Field(..., description="Whether users can input text to the system")
    produces_output_used_in_decisions: bool = Field(..., description="Whether AI output influences real decisions")
    has_access_to_external_systems: bool = Field(..., description="Whether AI can call APIs or access databases")

# Response model for OWASP check
class OWASPResponse(BaseModel):
    system_name: str
    risks_found: List[str]
    severity_level: str
    recommendations: List[str]

# Request model for full assessment pipeline
class FullAssessmentRequest(BaseModel):
    system_name: str
    description: str
    sector: str
    automated_decision: bool
    processes_personal_data: bool
    interacts_with_humans: bool
    uses_llm: bool
    accepts_user_input: bool
    data_subjects: Optional[str] = None
    data_types: Optional[str] = None
    processing_purpose: Optional[str] = None

# Response model for full assessment
class FullAssessmentResponse(BaseModel):
    system_name: str
    classification: ClassificationResponse
    dpia: DPIAResponse
    owasp: OWASPResponse
    report_id: str
    report_download_url: str