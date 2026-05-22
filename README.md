# EU AI Act Governance Platform

<div align="center">

![Platform Logo](https://img.shields.io/badge/EU_AI_Act-Governance_Platform-003399?style=for-the-badge&logo=europeanunion&logoColor=FFCC00)

*An open-source enterprise platform that automates AI governance and compliance for organisations deploying AI systems under the EU AI Act (Regulation EU 2024/1689), GDPR, and NIST AI RMF.*

---

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![LangChain](https://img.shields.io/badge/LangChain-1C3C3A?style=for-the-badge&logo=chainlink&logoColor=white)](https://github.com/langchain-ai/langchain)

[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white)](https://kubernetes.io)
[![Terraform](https://img.shields.io/badge/Terraform-7B42BC?style=for-the-badge&logo=terraform&logoColor=white)](https://www.terraform.io)
[![Azure AKS](https://img.shields.io/badge/Azure_AKS-0089D6?style=for-the-badge&logo=microsoftazure&logoColor=white)](https://azure.microsoft.com/en-us/products/kubernetes-service)

[![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?style=for-the-badge&logo=prometheus&logoColor=white)](https://prometheus.io)
[![Grafana](https://img.shields.io/badge/Grafana-F46800?style=for-the-badge&logo=grafana&logoColor=white)](https://grafana.com)
[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)](https://github.com/features/actions)

</div>

---

## 🔍 The Problem

Organisations deploying Artificial Intelligence systems within the European single market face significant regulatory hurdles under the **EU AI Act**. Compliance assessment is historically manual, slow, fragmented, and prone to human error, creating a massive bottleneck for companies (especially SMEs) seeking to deploy AI safely and legally.

This platform bridges that gap by **automating and standardising AI compliance** into a unified, high-performance DevSecOps framework.

---

## 🚀 Key Platform Features

* **EU AI Act Classifier**: Automatically classifies AI systems into risk tiers (*Unacceptable / High / Limited / Minimal*) based on technical characteristics, utilizing official article cross-references.
* **GDPR DPIA Generator**: Automatically drafts pre-filled Data Protection Impact Assessments aligned with **GDPR Article 35** for systems processing personal data.
* **Security & Vulnerability Scanners**:
  * Evaluates LLM-based systems against the **OWASP LLM Top 10** risks.
  * Cross-checks software bills-of-materials (SBOM) against the National Vulnerability Database (**NVD**) and **MITRE ATLAS** frameworks.
* **Observability Dashboard**: Built-in Prometheus and Grafana panels displaying real-time compliance trends, system health, request rates, latencies, and risk tier distributions.
* **RAG Compliance Assistant**: Chat assistant powered by Azure OpenAI and LangChain, enabling developers to ask complex legal compliance questions directly from the codebase.
* **Enterprise DevSecOps Pipeline**: Secure, containerized pipeline enforcing security scans (SAST, SCA, container scanning, and DAST) on every build push.

---

## ⚙️ Technology Stack

| Layer | Tools & Technologies |
|---|---|
| **Backend API** | Python 3.11, FastAPI, Pydantic, SQLAlchemy, Uvicorn |
| **Artificial Intelligence** | Azure OpenAI, LangChain, RAG Knowledge Base, FastEmbed |
| **Database** | PostgreSQL (Local / Azure Database for PostgreSQL) |
| **Observability** | Prometheus, Grafana, Prometheus FastAPI Instrumentator |
| **Infrastructure-as-Code** | Terraform, Azure Provider |
| **Containerization** | Docker, Kubernetes, AKS (Azure Kubernetes Service), ACR |
| **Continuous Integration** | GitHub Actions, Semgrep (SAST), Bandit (SAST), Syft (SCA), Trivy |

---

## 📈 Project Status & Roadmap

The platform is designed and constructed in organized, sprint-based phases. 

| Phase / Sprint | Focus Area | Status |
|---|---|---|
| **Phase 0** | Requirements, Architecture, STRIDE Threat Modeling | ✅ Complete |
| **Sprint 1** | Cloud Infrastructure (Terraform & Azure Setup) | ✅ Complete |
| **Sprint 2** | DevSecOps Secure CI/CD Pipelines | ✅ Complete |
| **Sprint 3** | Compliance Governance & Classification Engine | ✅ Complete |
| **Sprint 4** | AI Integrations (RAG Knowledge Assistant) | ✅ Complete |
| **Sprint 5** | Kubernetes Deployments & Grafana Observability | ✅ Complete |
| **Sprint 6** | Polish, Audits & Multi-language Reporting | ⏳ Pending |

### Completed Milestones
- [x] EU AI Act risk classification engine
- [x] GDPR DPIA report generator
- [x] OWASP LLM Top 10 assessment module
- [x] MITRE ATLAS & NVD dependency checkers
- [x] PDF compliance certificate exporter
- [x] Secure DevSecOps CI/CD scanning pipeline
- [x] RAG compliance chat assistant
- [x] Prometheus & Grafana automated observability stack
- [x] Production-ready Kubernetes (AKS) manifests

### Current Backlog
- [ ] Multi-language report support (German, French, Spanish)
- [ ] API versioning and automated public Swagger documentation
- [ ] Cryptographically signed audit log ledger for compliance compliance audits

---

## 🗺️ System Architecture

The platform partitions trust into three distinct isolation boundaries: the **Internet Boundary** (ingress traffic), the **Internal Service Mesh Boundary** (FastAPI backend and Prometheus), and the **Data Layer Boundary** (isolated SQL database and Key Vault).

* Visualise the structural network details and threat boundaries under `docs/architecture.html`.

---

## 📂 Core Documentation

| Resource | Description |
|---|---|
| 📄 **[Project Charter](docs/project-charter.md)** | Scope statement, business goals, and timeline milestones. |
| 📄 **[System Requirements](docs/requirements.md)** | Functional and non-functional engineering requirements. |
| 📄 **[STRIDE Threat Model](docs/threat-model.md)** | OWASP Threat Dragon STRIDE analysis and full risk mitigation register. |
| 📄 **[ADR 001 — Framework Decision](docs/adr/adr-001-fastapi-over-flask.md)** | Choosing FastAPI over Flask for async, high-concurrency compliance routines. |
| 📄 **[ADR 002 — IaC Decision](docs/adr/adr-002-terraform-over-bicep.md)** | Standardising on Terraform over Bicep for multi-cloud readiness. |
| 📄 **[ADR 003 — Orchestration](docs/adr/adr-003-aks-over-container-apps.md)** | Selecting AKS (Azure Kubernetes Service) for enterprise scaling. |
| 📄 **[ADR 004 — Persistent Data](docs/adr/adr-004-postgresql-over-cosmosdb.md)** | Leveraging relational PostgreSQL for transactional audit trails. |

---

## 🔐 Security Posture & Standards

Security is baked directly into the development cycle:
* **Pre-Development Threat Modeling**: All potential vectors were analyzed using a STRIDE framework before a single line of backend logic was introduced.
* **Static Application Security Testing (SAST)**: Automated linting and security vulnerability scanning using Bandit and Semgrep.
* **Software Composition Analysis (SCA)**: Automatic SBOM (Software Bill of Materials) generation using Syft, with vulnerability checking powered by Grype.
* **Container Scanning**: Every container image built is vetted by Trivy to prevent base-image dependency vulnerabilities.
* **DAST Scans**: Staging endpoints undergo regular dynamic testing using OWASP ZAP scanners.
* **Secret Management**: API keys, database credentials, and certificates are managed exclusively inside Azure Key Vault (no hardcoded environment keys).

---

## 🛠️ Quick Start (Local Docker Compose)

You can launch the entire compliance platform, database, and telemetry dashboard locally in less than 2 minutes.

### 1. Configure the Environment
Ensure you have a `.env` file populated at the project root with your credentials:
```env
DB_USER=pgadmin
DB_PASSWORD=Shahriyar@1998#
DB_NAME=euaigovernance
GROQ_API_KEY=your_groq_api_key
HF_API_KEY=your_huggingface_key
JWT_SECRET=minimum_32_characters_random_string
```

### 2. Launch Services
Run the following Docker Compose command to build and launch all containers:
```bash
docker compose up --build -d
```

### 3. Access Interfaces
* **FastAPI Backend (Swagger API Docs)**: [http://localhost:8000/docs](http://localhost:8000/docs)
* **Prometheus Engine**: [http://localhost:9090](http://localhost:9090)
* **Grafana Dashboard**: [http://localhost:3000](http://localhost:3000) *(User: `admin` / Password: `admin`)*
  * Navigate to **Dashboards** > **Observability** > **EU AI Act Governance Observability** to view real-time compliance telemetry.

---

## 🤝 Contributing

We welcome global contributions from AI policy experts, security engineers, and compliance automation developers. 

Please read **[CONTRIBUTING.md](CONTRIBUTING.md)** before opening issues or submitting pull requests.

---

## ⚖️ Licence

This project is licensed under the **MIT License** — feel free to use, modify, and distribute for corporate or individual deployments.

---

<div align="center">

**Built with 💻 by [Farhan Shahriyar](https://linkedin.com/in/farhanshahriyar) — Hamburg, Germany**

*If this platform helps your organization navigate EU AI Act compliance, please consider giving us a ⭐ star on GitHub and sharing it with your network!*

</div>