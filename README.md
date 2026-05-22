# EU AI Act Governance Platform

<div align="center">

![Platform](https://img.shields.io/badge/EU_AI_Act-Governance_Platform-003399?style=for-the-badge&logo=europeanunion&logoColor=FFCC00)

**An open-source platform that automates AI compliance for the EU AI Act (Regulation EU 2024/1689), GDPR, and NIST AI RMF.**

[**Live Demo →**](https://eu-ai-governance.salmonocean-15ddaf55.germanywestcentral.azurecontainerapps.io) · [Documentation](docs/) · [Report Bug](https://github.com/Shahriyar31/eu-ai-act-governance-platform/issues)

---

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)](https://www.docker.com)
[![Terraform](https://img.shields.io/badge/Terraform-7B42BC?style=flat-square&logo=terraform&logoColor=white)](https://www.terraform.io)
[![Azure](https://img.shields.io/badge/Azure_Container_Apps-0089D6?style=flat-square&logo=microsoftazure&logoColor=white)](https://azure.microsoft.com/en-us/products/container-apps)
[![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?style=flat-square&logo=prometheus&logoColor=white)](https://prometheus.io)
[![Grafana](https://img.shields.io/badge/Grafana-F46800?style=flat-square&logo=grafana&logoColor=white)](https://grafana.com)
[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=flat-square&logo=githubactions&logoColor=white)](https://github.com/features/actions)
[![MIT License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

</div>

---

## The Problem

Organisations deploying AI systems inside the EU face a hard compliance deadline. The EU AI Act requires risk classification, documentation, and impact assessments before deployment — but the process is manual, slow, and expensive. For most teams, compliance is an afterthought bolted on at the end.

This platform makes compliance a first-class engineering concern: automated, auditable, and integrated directly into the development pipeline.

---

## What It Does

Submit an AI system's description and technical characteristics. The platform returns a full compliance report in seconds.

| Feature | What it automates |
|---|---|
| **EU AI Act Risk Classifier** | Classifies AI systems into Unacceptable / High / Limited / Minimal risk tiers with article-level justification |
| **GDPR DPIA Generator** | Drafts Data Protection Impact Assessments aligned with GDPR Article 35 |
| **OWASP LLM Top 10 Checker** | Evaluates LLM-based systems against the 10 most critical LLM security risks |
| **NIST AI RMF Mapper** | Maps system characteristics to NIST AI Risk Management Framework controls |
| **NVD Vulnerability Scanner** | Cross-checks software dependencies against the National Vulnerability Database |
| **MITRE ATLAS Threat Assessment** | Identifies adversarial ML threats relevant to the system's architecture |
| **PDF Report Generator** | Exports a complete compliance certificate covering all above assessments |
| **RAG Compliance Assistant** | Answers EU AI Act questions grounded in the regulation text via LangChain + Groq |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Internet Boundary                         │
│                                                             │
│   Browser / API Client                                      │
│        │                                                    │
│        ▼                                                    │
│   Azure Container Apps (HTTPS, TLS termination)             │
│   ┌────────────────────────────────────────────────────┐   │
│   │  React Frontend (Vite)                             │   │
│   │  FastAPI Backend (Python 3.11)                     │   │
│   │    ├── /api/v1/classify      EU AI Act classifier  │   │
│   │    ├── /api/v1/dpia          DPIA generator        │   │
│   │    ├── /api/v1/owasp-check   OWASP LLM scanner     │   │
│   │    ├── /api/v1/nvd-check     NVD vulnerability scan │   │
│   │    ├── /api/v1/atlas-check   MITRE ATLAS threats   │   │
│   │    ├── /api/v1/assess-and-download  Full PDF report │   │
│   │    ├── /api/v1/ai/chat       RAG compliance chat   │   │
│   │    └── /metrics              Prometheus scrape     │   │
│   └────────────────────────────────────────────────────┘   │
│                                                             │
│   ┌──────────────┐    ┌──────────────────────────────────┐ │
│   │  Prometheus  │───▶│  Grafana Observability Dashboard  │ │
│   │  (scrapes    │    │  - API health & uptime            │ │
│   │   /metrics)  │    │  - Request rate & latency (RED)   │ │
│   └──────────────┘    │  - Compliance assessment counters │ │
│                       └──────────────────────────────────┘ │
│                                                             │
│   Azure Database for PostgreSQL                             │
│   Azure Key Vault (secrets)                                 │
│   Azure Container Registry (image storage)                  │
└─────────────────────────────────────────────────────────────┘
```

Full architecture diagram: [docs/architecture.html](docs/architecture.html)

---

## DevSecOps Pipeline

Every push to `main` runs a four-stage security pipeline before any image reaches production:

```
Push to main
    │
    ├── SAST ──────────────── Bandit + Semgrep (static code analysis)
    │
    ├── SCA ───────────────── pip-audit + Syft (SBOM) + Grype (CVE scan)
    │
    ├── Container Scan ─────── Trivy (image CVE scan, blocks on CRITICAL)
    │
    └── Push to ACR ────────── Only runs if all three gates pass
```

Security findings from SAST and container scans are published to the GitHub Security tab via SARIF.

---

## Observability

The platform ships with a production-grade monitoring stack deployed to Azure Container Apps:

- **Prometheus** scrapes `/metrics` every 15 seconds
- **Grafana** dashboard covers three areas:

**System Health** — API status, uptime, memory usage (RSS), CPU load

**RED Method** — Request rate (QPS), HTTP latency (p50/p90/p99), throughput by endpoint

**Compliance Analytics** — Total assessments run, DPIA reports generated, OWASP scans, PDF exports, risk tier distribution

---

## Infrastructure

All cloud resources are provisioned via Terraform and stored as code:

| Resource | Purpose |
|---|---|
| Azure Container Apps | Hosts API, Prometheus, Grafana |
| Azure Database for PostgreSQL | Assessment history, user accounts |
| Azure Container Registry | Stores Docker images |
| Azure Key Vault | Secrets management |
| Azure Storage (remote state) | Terraform state backend |

Region: `germanywestcentral` — Frankfurt, Germany. Chosen for GDPR/BDSG alignment and EU data residency.

---

## Local Development

### Prerequisites

- Python 3.11+
- PostgreSQL running locally
- Docker (for image builds)

### Setup

```bash
git clone https://github.com/Shahriyar31/eu-ai-act-governance-platform.git
cd eu-ai-act-governance-platform
```

Create a `.env` file at the project root:

```env
DB_HOST=localhost
DB_PORT=5432
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_NAME=euaigovernance
GROQ_API_KEY=your_groq_api_key
JWT_SECRET=minimum_32_characters_random_string
```

Install dependencies and start the API:

```bash
pip install -r requirements.txt
uvicorn src.api.main:app --reload --port 8001
```

API docs available at: `http://localhost:8001/docs`

---

## Project Structure

```
eu-ai-act-governance-platform/
├── .github/workflows/ci.yaml
├── docker/Dockerfile
├── docs/
├── frontend/               React dashboard (Vite)
├── k8s/                    Kubernetes manifests
├── monitoring/
│   ├── prometheus/         Custom Prometheus image + config
│   └── grafana/            Custom Grafana image + dashboard JSON
├── src/
│   ├── api/main.py
│   ├── routers/
│   ├── governance/
│   ├── database/
│   ├── models/
│   └── metrics.py
├── terraform/
├── tests/
├── docker-compose.yml
└── requirements.txt
```

---

## Documentation

| Document | Description |
|---|---|
| [Project Charter](docs/project-charter.md) | Scope, goals, and timeline |
| [System Requirements](docs/requirements.md) | Functional and non-functional requirements |
| [STRIDE Threat Model](docs/threat-model.md) | Threat analysis and risk register |
| [ADR 001 — FastAPI over Flask](docs/adr/adr-001-fastapi-over-flask.md) | Framework decision |
| [ADR 002 — Terraform over Bicep](docs/adr/adr-002-terraform-over-bicep.md) | IaC decision |
| [ADR 003 — Container Apps over AKS](docs/adr/adr-003-aks-over-container-apps.md) | Deployment decision |
| [ADR 004 — PostgreSQL over CosmosDB](docs/adr/adr-004-postgresql-over-cosmosdb.md) | Database decision |

---

## Security

- Secrets managed exclusively via Azure Key Vault — no hardcoded credentials anywhere in the codebase
- JWT authentication on all governance endpoints
- SAST, SCA, and container scanning on every CI run
- STRIDE threat model completed before any backend logic was written
- TLS enforced at the Azure Container Apps ingress layer

To report a security vulnerability, open a private issue or contact via LinkedIn.

---

## License

MIT — free to use, modify, and distribute.

---

<div align="center">

Built by [Farhan Shahriyar](https://linkedin.com/in/farhanshahriyar) · Hamburg, Germany · MSc Data Science, TUHH

*If this project is useful to your organisation, a ⭐ on GitHub helps others find it.*

</div>