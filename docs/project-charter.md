# Project Charter — EU AI Act Governance Platform

**Version:** 1.0  
**Date:** May 2026  
**Author:** Farhan Shahriyar  
**Status:** Active  

---

## 1. Problem Statement

Organisations deploying AI systems across Europe face a growing 
regulatory burden under the EU AI Act (Regulation EU 2024/1689), 
GDPR, and NIST AI RMF. Currently, compliance assessment is done 
manually, inconsistently, and without a unified automated framework. 
There is no open-source tool that combines EU AI Act risk 
classification, DPIA generation, OWASP LLM Top 10 security 
assessment, and DevSecOps security scanning in a single deployable 
platform.

---

## 2. Objectives

- Automatically classify any AI system into the correct EU AI Act 
  risk tier (Unacceptable, High, Limited, Minimal) within 30 seconds
- Generate a complete pre-filled DPIA report without manual 
  intervention
- Assess AI systems against OWASP LLM Top 10 and NIST AI RMF
- Produce downloadable PDF compliance reports
- Implement a full DevSecOps pipeline with SAST, SCA, DAST, and 
  container scanning
- Deploy a production-grade platform on Azure using Terraform and 
  Kubernetes
- Provide a RAG-powered compliance assistant using Azure OpenAI
- Monitor platform health via Grafana and Azure Monitor

---

## 3. Scope

### In Scope
- EU AI Act risk tier classification engine
- Automated DPIA checklist generator
- OWASP LLM Top 10 assessment module
- NIST AI RMF alignment report
- PDF report generation
- Full CI/CD pipeline with SAST, SCA, DAST, SBOM generation
- Container vulnerability scanning with Trivy
- Azure cloud deployment via Terraform
- Kubernetes orchestration on AKS
- RAG-powered compliance Q&A assistant
- Grafana monitoring dashboard
- Full SDLC documentation

### Out of Scope
- Mobile application
- Multi-tenant SaaS platform
- Legal certification or advice
- Integration with third-party GRC tools (e.g. ServiceNow, Archer)
- Support for non-EU regulatory frameworks (beyond NIST AI RMF)

---

## 4. Tech Stack

| Layer | Technology |
|---|---|
| Infrastructure | Terraform, Azure |
| Containers | Docker, Kubernetes, AKS, ACR |
| CI/CD | GitHub Actions |
| SAST | Bandit, Semgrep |
| SCA | Syft, Grype, OWASP Dependency Check |
| DAST | OWASP ZAP |
| Container Scanning | Trivy |
| Backend | Python, FastAPI |
| AI | Azure OpenAI, LangChain, RAG |
| Database | PostgreSQL on Azure |
| Monitoring | Grafana, Azure Monitor |
| Security | Azure Key Vault, IAM/RBAC, VNet, NSGs |

---

## 5. Success Criteria

- [ ] All six sprints completed
- [ ] Full CI/CD pipeline operational with all security gates passing
- [ ] EU AI Act classifier correctly tiers at least 5 test AI systems
- [ ] DPIA report generated automatically without manual input
- [ ] OWASP ZAP DAST scan passes with no critical findings
- [ ] Application deployed and accessible on Azure Kubernetes Service
- [ ] Grafana dashboard operational with live metrics
- [ ] RAG assistant answers compliance questions accurately
- [ ] README and all documentation complete
- [ ] Demo video recorded and published

---

## 6. Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Azure free credits exhausted | Medium | High | Set budget alerts, monitor weekly |
| Kubernetes complexity delays timeline | High | Medium | Start with Docker Compose, migrate to AKS in Sprint 5 |
| Scope creep | High | High | Strictly follow Definition of Done per sprint |
| Terraform errors on Azure | Medium | Medium | Follow official Azure Terraform documentation |
| OWASP ZAP integration complexity | Medium | Low | Use ZAP Docker image with GitHub Actions |
| Azure OpenAI API costs | Medium | Medium | Use token limits and caching |

---

## 7. Timeline

| Sprint | Focus | Duration |
|---|---|---|
| Phase 0 | SDLC Documentation | Week 1-2 |
| Sprint 1 | Infrastructure & Containerisation | Week 3-4 |
| Sprint 2 | DevSecOps Pipeline | Week 5-6 |
| Sprint 3 | Governance Engine | Week 7-9 |
| Sprint 4 | AI Integration | Week 10-11 |
| Sprint 5 | Kubernetes & Monitoring | Week 12-13 |
| Sprint 6 | Polish & Documentation | Week 14 |

---

## 8. Definition of Done

A feature is only complete when:
- Code is written and works as expected
- Unit tests are written and passing
- Security scan shows no critical findings
- Documentation is updated
- Changes are committed with a meaningful commit message
- Feature is deployed and verified in the environment

---

---

## 9. Vision

The EU AI Act represents the world's first comprehensive legal 
framework for artificial intelligence. Most organisations — 
especially SMEs — lack the tools and resources to assess compliance 
systematically.

This platform aims to be a free, open-source solution that makes 
EU AI Act compliance accessible to any organisation deploying AI 
systems. It is built in public, documented transparently, and open 
to community contributions.

If you are working on AI governance, compliance automation, or 
DevSecOps and want to contribute — open an issue or start a 
discussion. Every perspective makes this better.

**Built by Farhan Shahriyar — Hamburg, Germany.**