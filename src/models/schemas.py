from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class SectorEnum(str, Enum):
    healthcare = "healthcare"
    employment = "employment"
    education = "education"
    law_enforcement = "law_enforcement"
    border_control = "border_control"
    critical_infrastructure = "critical_infrastructure"
    justice = "justice"
    finance = "finance"
    other = "other"

class RiskTierEnum(str, Enum):
    unacceptable = "unacceptable"
    high = "high"
    limited = "limited"
    minimal = "minimal"

class ClassificationRequest(BaseModel):
    system_name: str = Field(..., description="Name of the AI system being assessed")
    description: str = Field(..., description="What the AI system does")
    sector: SectorEnum = Field(..., description="Sector the AI system operates in")
    automated_decision: bool = Field(..., description="Makes decisions without human review")
    processes_personal_data: bool = Field(..., description="Processes personal data of individuals")
    interacts_with_humans: bool = Field(..., description="Directly interacts with humans")

class ClassificationResponse(BaseModel):
    system_name: str
    risk_tier: RiskTierEnum
    justification: str
    obligations: List[str]
    dpia_required: bool

class DPIARequest(BaseModel):
    system_name: str
    description: str
    sector: SectorEnum
    data_subjects: str = Field(..., description="Who the personal data belongs to")
    data_types: str = Field(..., description="What personal data is processed")
    processing_purpose: str = Field(..., description="Why the data is being processed")
    risk_tier: RiskTierEnum = Field(..., description="Risk tier from classification")

class DPIAResponse(BaseModel):
    system_name: str
    dpia_required: bool
    assessment_summary: str
    risks_identified: List[str]
    mitigation_measures: List[str]
    recommendation: str

class OWASPRequest(BaseModel):
    system_name: str
    description: str
    uses_llm: bool = Field(..., description="Whether the system uses a large language model")
    accepts_user_input: bool = Field(..., description="Whether users can input text to the system")
    produces_output_used_in_decisions: bool = Field(..., description="Whether AI output influences real decisions")
    has_access_to_external_systems: bool = Field(..., description="Whether AI can call APIs or access databases")

class OWASPResponse(BaseModel):
    system_name: str
    risks_found: List[str]
    severity_level: str
    recommendations: List[str]

class FullAssessmentRequest(BaseModel):
    system_name: str
    description: str
    sector: SectorEnum
    automated_decision: bool
    processes_personal_data: bool
    interacts_with_humans: bool
    uses_llm: bool
    accepts_user_input: bool
    data_subjects: Optional[str] = None
    data_types: Optional[str] = None
    processing_purpose: Optional[str] = None
    language: Optional[str] = "en"

class FullAssessmentResponse(BaseModel):
    system_name: str
    classification: ClassificationResponse
    dpia: DPIAResponse
    owasp: OWASPResponse
    report_id: str
    report_download_url: str

class NVDCheckRequest(BaseModel):
    system_name: str
    technologies: List[str] = Field(
        ...,
        description="List of technologies used — e.g. ['tensorflow 2.10', 'pytorch 1.12']"
    )

class NVDCheckResponse(BaseModel):
    system_name: str
    technologies_checked: List[str]
    critical_count: int
    high_count: int
    medium_count: int
    overall_risk: str
    recommendations: List[str]


class ATLASCheckRequest(BaseModel):
    system_name: str
    uses_llm: bool
    accepts_user_input: bool
    has_external_api: bool
    processes_personal_data: bool
    automated_decision: bool

class ATLASCheckResponse(BaseModel):
    system_name: str
    techniques_found: int
    tactics_covered: List[str]
    risk_summary: str
    recommendations: List[str]
    technique_details: List[str]


class ClassificationRequestV2(BaseModel):
    system_name: str = Field(..., description="Name of the AI system being assessed")
    description: str = Field(..., description="What the AI system does")
    intended_purpose: str = Field(..., description="The specific intended clinical, industrial, or educational purpose of the AI")
    sector: SectorEnum = Field(..., description="Sector the AI system operates in")
    automated_decision: bool = Field(..., description="Makes decisions without human review")
    processes_personal_data: bool = Field(..., description="Processes personal data of individuals")
    interacts_with_humans: bool = Field(..., description="Directly interacts with humans")


class ClassificationResponseV2(BaseModel):
    system_name: str
    risk_tier: RiskTierEnum
    justification: str
    obligations: List[str]
    dpia_required: bool
    intended_purpose: str
    regulatory_framework: str = "EU AI Act 2024 (Reg. EU 2024/1689)"


    