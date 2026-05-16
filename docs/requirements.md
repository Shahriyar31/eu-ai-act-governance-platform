# Requirements Engineering — EU AI Act Governance Platform

**Version:** 1.0  
**Date:** May 2026  
**Author:** Farhan Shahriyar  
**Status:** Active  

---

## 1. Functional Requirements

### 1.1 EU AI Act Risk Classification
- The system shall accept input describing an AI system including 
  its purpose, domain, and capabilities
- The system shall classify the AI system into one of four EU AI 
  Act risk tiers: Unacceptable, High, Limited, or Minimal
- The system shall provide a justification for the classification 
  referencing specific EU AI Act articles
- The system shall complete classification within 30 seconds

### 1.2 DPIA Generator
- The system shall generate a pre-filled Data Protection Impact 
  Assessment based on the AI system description
- The system shall align the DPIA to GDPR Article 35 requirements
- The system shall output the DPIA as a downloadable PDF report
- The system shall highlight areas requiring manual review

### 1.3 OWASP LLM Top 10 Assessment
- The system shall assess any LLM-based AI system against all 10 
  OWASP LLM vulnerabilities
- The system shall provide a risk rating for each vulnerability
- The system shall suggest remediation steps for each finding

### 1.4 NIST AI RMF Alignment
- The system shall map AI system characteristics to NIST AI RMF 
  core functions: Govern, Map, Measure, Manage
- The system shall generate an alignment report with gaps identified

### 1.5 PDF Report Generation
- The system shall generate a unified compliance report combining 
  EU AI Act classification, DPIA, OWASP assessment, and NIST 
  alignment
- The report shall be downloadable in PDF format
- The report shall include a compliance score and summary dashboard

### 1.6 RAG Compliance Assistant
- The system shall provide a conversational interface for 
  compliance questions
- The assistant shall answer questions using EU AI Act, GDPR, 
  NIST AI RMF, and OWASP LLM Top 10 as its knowledge base
- The assistant shall cite specific articles and requirements in 
  its answers
- The assistant shall be evaluated using an LLM-as-judge framework

### 1.7 DevSecOps Pipeline
- The system shall run SAST on every code push using Bandit and 
  Semgrep
- The system shall run SCA on every code push using Syft, Grype, 
  and OWASP Dependency Check
- The system shall generate an SBOM on every build
- The system shall scan all Docker images using Trivy
- The system shall block builds when critical findings are detected
- The system shall run DAST using OWASP ZAP against the staging 
  environment on every pull request to main

### 1.8 Monitoring
- The system shall expose a Grafana dashboard with live metrics
- The system shall alert on API response times exceeding 3 seconds
- The system shall alert on container restarts
- The system shall log all compliance assessments for audit purposes

---

## 2. Non-Functional Requirements

### 2.1 Performance
- API response time shall not exceed 3 seconds for classification 
  requests
- PDF generation shall complete within 10 seconds
- The platform shall support at least 50 concurrent users

### 2.2 Security
- All secrets shall be stored in Azure Key Vault
- All data shall be encrypted at rest and in transit
- IAM and RBAC shall follow principle of least privilege
- No credentials shall ever be committed to GitHub

### 2.3 Reliability
- Platform uptime shall be 99.9%
- The system shall recover from pod failures automatically via 
  Kubernetes

### 2.4 Scalability
- The system shall scale horizontally via Kubernetes HPA
- The system shall handle traffic spikes without manual 
  intervention

### 2.5 Maintainability
- All code shall follow PEP 8 standards
- All functions shall have docstrings
- Test coverage shall be minimum 70%
- All infrastructure shall be defined as code via Terraform

### 2.6 Portability
- The entire application shall run in Docker containers
- The application shall be deployable on any Kubernetes cluster
- No vendor lock-in beyond Azure OpenAI for LLM capabilities

---

## 3. User Stories

### Epic 1 — Compliance Assessment
> As a compliance officer, I want to input my AI system details 
> and receive an EU AI Act risk classification so that I know my 
> regulatory obligations.

> As a data protection officer, I want an automatically generated 
> DPIA so that I can review and finalise it without starting from 
> scratch.

> As a security engineer, I want an OWASP LLM Top 10 assessment 
> so that I know which vulnerabilities to address before deployment.

### Epic 2 — DevSecOps
> As a developer, I want my code automatically scanned for 
> vulnerabilities on every push so that security issues are caught 
> early.

> As a DevSecOps engineer, I want builds blocked on critical 
> findings so that vulnerable code never reaches production.

> As a security analyst, I want an SBOM generated on every build 
> so that I have full visibility of software dependencies.

### Epic 3 — Compliance Assistant
> As a compliance officer, I want to ask natural language questions 
> about EU AI Act requirements so that I can get answers without 
> reading 100 pages of regulation.

### Epic 4 — Monitoring
> As a platform engineer, I want a Grafana dashboard showing 
> system health so that I can detect and respond to issues quickly.

---

## 4. Constraints

- Azure is the primary cloud provider
- Platform must be fully open source under MIT license
- Must be deployable by any organisation following the README
- All infrastructure must be defined as code — no manual 
  cloud configuration
- No credentials or secrets shall ever be hardcoded or 
  committed to the repository
- EU data residency must be respected — all data processed 
  and stored within EU Azure regions
- The platform must remain free to use for any organisation

---

## 5. Assumptions

- Azure OpenAI API access is available via GitHub Education credits
- EU AI Act Annex III high-risk categories are used for 
  classification logic
- Users have basic understanding of their AI system's purpose 
  and capabilities
- Community contributions will follow standard GitHub pull request 
  workflow

---

*Open to contributions — see CONTRIBUTING.md (coming soon)*