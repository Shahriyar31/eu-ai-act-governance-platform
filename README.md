# EU AI Act Governance Platform

> An open-source platform that automates AI governance and 
> compliance for organisations deploying AI systems under 
> the EU AI Act, GDPR, and NIST AI RMF.

---

## The Problem

Organisations deploying AI systems across Europe face a growing
regulatory burden under the EU AI Act (Regulation EU 2024/1689).
Compliance assessment is currently done manually, inconsistently,
and without a unified automated framework.

Most companies — especially SMEs — lack the tools to assess
compliance systematically. This platform aims to change that.

---

## What This Platform Does

- Automatically classifies AI systems into EU AI Act risk tiers
  (Unacceptable / High / Limited / Minimal) with article references
- Generates pre-filled DPIA reports aligned to GDPR Article 35
- Assesses LLM-based systems against OWASP LLM Top 10
- Maps AI systems to NIST AI RMF core functions
- Produces downloadable PDF compliance reports
- Provides a RAG-powered compliance assistant using Azure OpenAI
- Runs a full DevSecOps security pipeline on every code push

---

## Tech Stack

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
| Security | Azure Key Vault, IAM/RBAC, VNet |

---

## Project Status

🚧 **Currently in active development — Phase 0 (SDLC Documentation)**

| Phase | Status |
|---|---|
| Project Charter | ✅ Complete |
| Requirements Engineering | ✅ Complete |
| Architecture Design | ✅ Complete |
| Threat Modelling | ✅ Complete |
| Technology Decision Records | ✅ Complete |
| Sprint 1 — Infrastructure | 🔄 Starting |
| Sprint 2 — DevSecOps Pipeline | ⏳ Pending |
| Sprint 3 — Governance Engine | ⏳ Pending |
| Sprint 4 — AI Integration | ⏳ Pending |
| Sprint 5 — Kubernetes & Monitoring | ⏳ Pending |
| Sprint 6 — Polish & Documentation | ⏳ Pending |

---

## Architecture

The platform follows a microservices architecture with three
clear trust boundaries — Internet, Internal Network, and
Data Layer — all deployed on Azure via Terraform.

See the full architecture diagrams in
[docs/architecture.html](docs/architecture.html)

---

## Documentation

| Document | Description |
|---|---|
| [Project Charter](docs/project-charter.md) | Project scope, objectives, risks, and timeline |
| [Requirements](docs/requirements.md) | Functional and non-functional requirements |
| [Architecture](docs/architecture.html) | Full system architecture diagrams |
| [Threat Model](docs/threat-model.md) | STRIDE threat model with full threat register |
| [ADR 001](docs/adr/adr-001-fastapi-over-flask.md) | FastAPI over Flask |
| [ADR 002](docs/adr/adr-002-terraform-over-bicep.md) | Terraform over Bicep |
| [ADR 003](docs/adr/adr-003-aks-over-container-apps.md) | AKS over Container Apps |
| [ADR 004](docs/adr/adr-004-postgresql-over-cosmosdb.md) | PostgreSQL over CosmosDB |

---

## Security

This project takes security seriously. Before any code was
written, a full STRIDE-based threat model was produced using
OWASP Threat Dragon identifying 10 threats across all system
components.

Security is enforced at every layer:
- Threat modelling before development
- SAST on every code push
- SCA and SBOM generation on every build
- Container scanning with Trivy
- DAST with OWASP ZAP on every staging deployment
- Secrets managed exclusively via Azure Key Vault

---

## Contributing

This project is built in public and welcomes contributions.

If you work in AI governance, compliance automation, or
DevSecOps and want to contribute — open an issue or start
a discussion.

Areas where contributions are especially welcome:
- Additional EU AI Act Annex III classification rules
- Support for other regulatory frameworks
- Translations of the compliance reports
- Testing and bug reports

Please read [CONTRIBUTING.md](CONTRIBUTING.md) before
submitting a pull request.

---

## Roadmap

- [ ] EU AI Act risk classification engine
- [ ] DPIA report generator
- [ ] OWASP LLM Top 10 assessment module
- [ ] NIST AI RMF alignment report
- [ ] PDF report generation
- [ ] Full DevSecOps CI/CD pipeline
- [ ] Azure Kubernetes Service deployment
- [ ] RAG compliance assistant
- [ ] Grafana monitoring dashboard
- [ ] Multi-language report support
- [ ] API documentation via Swagger

---

## Licence

MIT — free to use, modify, and distribute.

---

**Built by [Farhan Shahriyar](https://linkedin.com/in/farhanshahriyar)
— Hamburg, Germany**

*If this project helps your organisation with EU AI Act compliance,
consider starring the repository and sharing it with your network.*