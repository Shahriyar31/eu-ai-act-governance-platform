# Argus AI — EU AI Act Governance Platform

<div align="center">

![Argus AI](https://img.shields.io/badge/Argus_AI-EU_AI_Act_Governance-1d6ef5?style=for-the-badge&logo=europeanunion&logoColor=white)

**An open-source, production-grade AI compliance platform that automates EU AI Act (Regulation EU 2024/1689), GDPR, and NIST AI RMF compliance — end to end.**

[**Live Platform →**](https://eu-ai-governance.salmonocean-15ddaf55.germanywestcentral.azurecontainerapps.io) · [API Docs](https://eu-ai-governance.salmonocean-15ddaf55.germanywestcentral.azurecontainerapps.io/docs) · [Report Bug](https://github.com/Shahriyar31/eu-ai-act-governance-platform/issues)

---

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL+pgvector-4169E1?style=flat-square&logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agent-FF6B35?style=flat-square)](https://langchain-ai.github.io/langgraph)
[![Groq](https://img.shields.io/badge/Groq-llama--3.3--70b-F55036?style=flat-square)](https://groq.com)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)](https://www.docker.com)
[![Terraform](https://img.shields.io/badge/Terraform-7B42BC?style=flat-square&logo=terraform&logoColor=white)](https://www.terraform.io)
[![Azure](https://img.shields.io/badge/Azure_Container_Apps-0089D6?style=flat-square&logo=microsoftazure&logoColor=white)](https://azure.microsoft.com)
[![Sentry](https://img.shields.io/badge/Sentry-362D59?style=flat-square&logo=sentry&logoColor=white)](https://sentry.io)
[![Cloudflare](https://img.shields.io/badge/Cloudflare_AI_Gateway-F38020?style=flat-square&logo=cloudflare&logoColor=white)](https://developers.cloudflare.com/ai-gateway)
[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=flat-square&logo=githubactions&logoColor=white)](https://github.com/features/actions)
[![MIT License](https://img.shields.io/badge/License-MIT-10b981?style=flat-square)](LICENSE)

</div>

---

## The Problem

Organisations deploying AI systems inside the EU face a hard compliance deadline. The EU AI Act requires risk classification, documentation, and impact assessments before deployment — but the process is manual, slow, and expensive. Legal teams charge thousands per assessment. Engineers have no tooling.

Argus AI makes compliance a first-class engineering concern: automated, auditable, observable, and integrated directly into the development pipeline.

---

## What It Does

Submit an AI system description and technical characteristics. The platform returns a full compliance report in seconds, writes a tamper-evident audit record, and monitors EUR-Lex for regulatory changes — automatically.

### Core Compliance Engine

| Module | What it automates |
|---|---|
| **EU AI Act Risk Classifier** | Rule-engine + LLM hybrid classifies AI systems into Unacceptable / High / Limited / Minimal risk tiers with article-level justification. 41 live rules stored in PostgreSQL — zero hardcoded logic |
| **GDPR DPIA Generator** | Drafts Data Protection Impact Assessments aligned with GDPR Article 35, including data subjects, processing risks, and mitigation measures |
| **OWASP LLM Top 10 Checker** | Evaluates LLM-based systems against prompt injection, training data poisoning, model DoS, and 7 other critical risks |
| **NIST AI RMF Mapper** | Maps system characteristics to NIST AI Risk Management Framework functions: Govern, Map, Measure, Manage |
| **NVD Vulnerability Scanner** | Cross-checks software dependencies against the National Vulnerability Database for known CVEs |
| **MITRE ATLAS Assessment** | Identifies adversarial ML threats relevant to the system architecture |
| **PDF Compliance Report** | Exports a complete compliance certificate covering all assessments, risk tiers, and recommendations |

### AI Integration

| Component | Details |
|---|---|
| **RAG Compliance Assistant** | Retrieval-augmented generation over 665+ EU AI Act document chunks stored in pgvector. Answers compliance questions with source citations |
| **LLM Fallback Chain** | Groq llama-3.3-70b-versatile → Gemini 2.5 Flash → Groq llama-3.1-8b-instant. Automatic failover with graceful 429 handling |
| **LangGraph Compliance Agent** | StateGraph with classify → router → dpia → owasp → summary nodes. Conditional routing by risk tier. Human-in-the-loop via interrupt() for HIGH/LIMITED risk assessments |
| **Cloudflare AI Gateway** | All LLM traffic routed through Cloudflare AI Gateway for caching, rate limiting, and cost observability |
| **RAGAS Evaluation** | Automated RAG quality evaluation — Answer Relevancy: 0.75, Context Precision: 0.70, Context Recall: 0.73 |

### Platform Features

| Feature | Details |
|---|---|
| **Regulatory Change Monitoring** | Monitors EUR-Lex, EU AI Office, and EU AI Act Reference Portal via Firecrawl. Detects changes via SHA-256 content hashing. Auto-updates knowledge base and emails org admins via Resend |
| **Audit Trail PDF Export** | SHA-256 hash-chained audit ledger. Every classification writes a tamper-evident record. Export as PDF for regulatory authorities |
| **Multi-tenancy** | Organisation model with slug, plan, and role-based access. Full org isolation on assessment history and classifications |
| **JWT Authentication** | Access tokens (15 min) + refresh tokens (7 days) with rotation and revocation. Rate limiting via SlowAPI |
| **Sentry Monitoring** | Production error tracking with full tracebacks, performance tracing at 10% sample rate |

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                         Internet Boundary                            │
│                                                                      │
│   Browser / API Client                                               │
│        │                                                             │
│        ▼                                                             │
│   Azure Container Apps (HTTPS, TLS termination, germanywestcentral)  │
│   ┌──────────────────────────────────────────────────────────────┐   │
│   │  React Frontend (Vite + Framer Motion)                       │   │
│   │  FastAPI Backend (Python 3.11)                               │   │
│   │    ├── /api/v1/classify          EU AI Act risk classifier   │   │
│   │    ├── /api/v1/dpia              DPIA generator              │   │
│   │    ├── /api/v1/owasp-check       OWASP LLM scanner           │   │
│   │    ├── /api/v1/nvd-check         NVD vulnerability scan      │   │
│   │    ├── /api/v1/atlas-check       MITRE ATLAS threats         │   │
│   │    ├── /api/v1/assess-and-download  Full PDF report          │   │
│   │    ├── /api/v1/ai/ask            RAG compliance assistant    │   │
│   │    ├── /api/v1/agent/assess      LangGraph compliance agent  │   │
│   │    ├── /api/v1/agent/assess/respond  Human-in-the-loop reply │   │
│   │    ├── /api/v1/monitoring/check  Regulatory change check     │   │
│   │    ├── /api/v1/audit/export      Tamper-evident PDF export   │   │
│   │    ├── /auth/*                   JWT auth + refresh + logout │   │
│   │    └── /metrics                  Prometheus scrape endpoint  │   │
│   └──────────────────────────────────────────────────────────────┘   │
│                │                                                      │
│                ▼                                                      │
│   ┌─────────────────────┐    ┌────────────────────────────────────┐  │
│   │  Cloudflare AI      │───▶│  Groq API (llama-3.3-70b)          │  │
│   │  Gateway            │    │  Gemini 2.5 Flash (fallback)       │  │
│   │  (caching + limits) │    │  Groq llama-3.1-8b (fallback)      │  │
│   └─────────────────────┘    └────────────────────────────────────┘  │
│                                                                      │
│   Azure Database for PostgreSQL (germanywestcentral)                 │
│   ├── classification_rules   41 live EU AI Act rules                 │
│   ├── chunk_embeddings       665+ pgvector chunks (384-dim)          │
│   ├── audit_ledger           SHA-256 hash-chained records            │
│   ├── assessment_history     org-isolated history                    │
│   ├── monitoring_sources     EUR-Lex, EU AI Office, etc.             │
│   ├── regulatory_updates     detected change records                 │
│   └── organisations + users + refresh_tokens                         │
│                                                                      │
│   Prometheus + Sentry ──▶ Grafana Observability Dashboard            │
│   Azure Container Registry · Azure Key Vault · Azure Storage         │
└──────────────────────────────────────────────────────────────────────┘
```

---

## DevSecOps Pipeline

Every push to `main` runs a five-stage security pipeline before any image reaches production:

```
Push to main
    │
    ├── SAST ──────────────── Bandit + Semgrep
    │                         Results → GitHub Security tab (SARIF)
    │
    ├── SCA ───────────────── pip-audit + Syft (SBOM) + Grype (CVE scan)
    │
    ├── Unit & Integration ── pytest with pgvector PostgreSQL service container
    │   Tests                 Alembic migrations run before test suite
    │
    ├── Container Scan ─────── Trivy (blocks on CRITICAL unfixed CVEs)
    │                         SARIF output → GitHub Security tab
    │
    └── Push to ACR ────────── Only runs if all four gates pass
         │
         └── CD ─────────────── az containerapp update (zero-downtime deploy)
```

The pipeline has executed **114+ runs** across all sprints.

---

## AI Stack

### LLM Fallback Chain

```
Request
    │
    ▼
Cloudflare AI Gateway
    ├── Groq llama-3.3-70b-versatile   [primary]
    │       ↓ on 429 / failure
    ├── Gemini 2.5 Flash               [secondary — optional]
    │       ↓ on failure
    └── Groq llama-3.1-8b-instant      [tertiary — always available]
```

### LangGraph Compliance Agent

```
User Input → classify_node → router_node
                                  │
              UNACCEPTABLE/MINIMAL │  HIGH/LIMITED
                     │             │
                     │    clarification_node [interrupt()]
                     │             │
                     │             ▼ (user responds via /agent/assess/respond)
                     │    dpia_node → owasp_node
                     │             │
                     └─────────────▼
                             summary_node → Full Compliance Report
```

State persisted via `MemorySaver` checkpointer. Thread IDs enable resume after human review.

### RAG Pipeline

```
Query → fastembed (BAAI/bge-small-en-v1.5) → pgvector similarity search
      → top-k context → Groq llama-3.3-70b → Answer with citations
```

RAGAS scores: Answer Relevancy **0.75** · Context Precision **0.70** · Context Recall **0.73**

---

## Regulatory Monitoring

```
Trigger (manual API or scheduled)
    │
    ▼
For each source (EUR-Lex, EU AI Office, EU AI Act Portal):
    ├── Firecrawl scrapes URL → markdown
    ├── SHA-256 hash compared to stored hash
    │       ├── Same → no change, update last_checked
    │       └── Different → CHANGE DETECTED:
    │               ├── Chunk + embed into pgvector
    │               ├── LLM summary of change
    │               ├── Write to regulatory_updates table
    │               └── Email org admins via Resend
    └── Continue to next source
```

---

## Audit Trail

Every classification writes a tamper-evident record:

```
record_hash = SHA-256(previous_hash + payload_json)
signature   = HMAC-SHA-256(JWT_SECRET, record_hash)
```

Modify any historical record → chain breaks → all subsequent hashes fail verification.

`GET /api/v1/audit/export` → downloadable PDF with chain integrity status per record.

---

## Observability

| Layer | Tool | Coverage |
|---|---|---|
| Infrastructure metrics | Prometheus + Grafana | QPS, latency p50/p90/p99, memory, CPU |
| Compliance analytics | Custom Prometheus counters | Risk tier distribution, DPIA count, PDF exports |
| Error tracking | Sentry | Full tracebacks, performance traces (10% sample rate) |
| LLM observability | Cloudflare AI Gateway | Token usage, cache hit rate, model latency |
| Structured logging | python-json-logger | JSON logs compatible with Azure Monitor |

---

## Infrastructure

All resources provisioned via Terraform with remote state in Azure Blob Storage.

| Resource | Purpose |
|---|---|
| Azure Container Apps | API + frontend, Prometheus, Grafana |
| Azure Database for PostgreSQL | All data + pgvector embeddings |
| Azure Container Registry | Docker image storage |
| Azure Key Vault | Secrets management |
| Azure Storage | Terraform state backend (versioned) |

**Region:** `germanywestcentral` (Frankfurt) — GDPR/BDSG alignment, EU data residency.

---

## Tech Stack

| Category | Technologies |
|---|---|
| **Backend** | Python 3.11, FastAPI, SQLAlchemy, Alembic, Pydantic v2 |
| **AI / LLM** | LangChain, LangGraph, Groq API, Gemini API, fastembed |
| **Vector DB** | PostgreSQL + pgvector (384-dimensional, 665+ chunks) |
| **RAG Evaluation** | RAGAS 0.2.15 |
| **Frontend** | React 18, Vite, Framer Motion, Lenis |
| **Auth** | JWT (access + refresh tokens), bcrypt, SlowAPI |
| **PDF Generation** | ReportLab |
| **Regulatory Monitoring** | Firecrawl, Resend |
| **Error Monitoring** | Sentry SDK (FastAPI integration) |
| **AI Gateway** | Cloudflare AI Gateway |
| **Observability** | Prometheus, Grafana, python-json-logger |
| **Infrastructure** | Terraform, Azure Container Apps, Azure PostgreSQL, ACR, Key Vault |
| **CI/CD** | GitHub Actions (5-stage pipeline) |
| **Security Scanning** | Bandit, Semgrep, pip-audit, Syft, Grype, Trivy |
| **Containerisation** | Docker (python:3.11-slim, layer-cache optimised) |

---

## Local Development

### Prerequisites

- Python 3.11+, PostgreSQL with pgvector, Docker, Node.js 20+

### Setup

```bash
git clone https://github.com/Shahriyar31/eu-ai-act-governance-platform.git
cd eu-ai-act-governance-platform
```

Create `.env`:

```env
DB_HOST=localhost
DB_PORT=5432
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_NAME=euaigovernance

JWT_SECRET=minimum_32_characters_random_string

GROQ_API_KEY=your_groq_api_key
GEMINI_API_KEY=your_gemini_api_key

CF_ACCOUNT_ID=your_cloudflare_account_id
CF_GATEWAY_NAME=your_gateway_name

FIRECRAWL_API_KEY=your_firecrawl_api_key
RESEND_API_KEY=your_resend_api_key
NOTIFICATION_EMAIL=your_email@example.com

SENTRY_DSN=your_sentry_dsn
```

```bash
psql -d euaigovernance -c "CREATE EXTENSION IF NOT EXISTS vector;"
pip install -r requirements.txt
alembic upgrade head
uvicorn src.api.main:app --reload --port 8001
```

Frontend Dashboard: `cd frontend && npm install && npm run dev`
Landing Page: `cd landing && npm install && npm run dev`

---

## Project Structure

```
eu-ai-act-governance-platform/
├── .github/workflows/      CI (ci.yaml) + CD (cd.yaml)
├── alembic/versions/       Database migrations
├── docker/Dockerfile       python:3.11-slim, layer-cache optimised
├── docs/                   Architecture, ADRs, threat model
├── frontend/               React dashboard (Vite)
├── landing/                Argus AI landing page (React + Framer Motion + Lenis)
├── monitoring/
│   ├── prometheus/         Custom Prometheus image + config
│   └── grafana/            Custom Grafana image + dashboard JSON
├── src/
│   ├── api/main.py         FastAPI app, lifespan, router registration
│   ├── routers/            governance, ai, agent, monitoring, auth, admin
│   ├── ai/                 llm_factory.py, rag_engine.py
│   ├── agents/             LangGraph StateGraph with human-in-the-loop
│   ├── governance/         classifier, dpia, owasp, nist, nvd, atlas, pdf
│   ├── monitoring/         regulatory_monitor.py (Firecrawl + Resend)
│   ├── reports/            audit_pdf.py (SHA-256 chain export)
│   ├── database/           models.py, connection.py, init_db.py
│   └── metrics.py          Prometheus custom counters
├── terraform/              Azure infrastructure as code
├── tests/                  Unit and integration tests
├── evaluate_rag.py         RAGAS evaluation script
├── ragas_results.json      Latest evaluation scores
└── requirements.txt
```

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/classify` | EU AI Act risk classification |
| POST | `/api/v1/dpia` | DPIA generation |
| POST | `/api/v1/owasp-check` | OWASP LLM Top 10 assessment |
| POST | `/api/v1/nvd-check` | NVD vulnerability scan |
| POST | `/api/v1/atlas-check` | MITRE ATLAS threat assessment |
| POST | `/api/v1/assess-and-download` | Full compliance PDF report |
| POST | `/api/v1/ai/ask` | RAG compliance assistant |
| POST | `/api/v1/agent/assess` | LangGraph agent (async for HIGH/LIMITED) |
| POST | `/api/v1/agent/assess/respond` | Resume after human review |
| POST | `/api/v1/monitoring/check` | Trigger regulatory source check |
| GET | `/api/v1/monitoring/sources` | List monitored sources |
| GET | `/api/v1/monitoring/updates` | List detected regulatory changes |
| GET | `/api/v1/audit/export` | Tamper-evident audit trail PDF |
| GET | `/api/v1/history` | Assessment history (org-scoped) |
| POST | `/auth/login` | JWT login |
| POST | `/auth/refresh` | Rotate access token |
| POST | `/auth/logout` | Revoke refresh token |
| GET | `/health` | Health check |
| GET | `/metrics` | Prometheus metrics |

---

## Security

- Secrets managed via Azure Key Vault — no hardcoded credentials in the codebase
- JWT access tokens (15 min) + refresh tokens (7 days) with rotation and revocation
- SAST, SCA, and container scanning on every CI run with SARIF to GitHub Security tab
- STRIDE threat model completed before any backend logic was written
- TLS enforced at Azure Container Apps ingress
- Rate limiting on all auth endpoints via SlowAPI
- All LLM traffic proxied through Cloudflare AI Gateway

---

## Documentation

| Document | Description |
|---|---|
| [Project Charter](docs/project-charter.md) | Scope, goals, timeline |
| [System Requirements](docs/requirements.md) | Functional and non-functional requirements |
| [STRIDE Threat Model](docs/threat-model.md) | Threat analysis and risk register |
| [Architecture Diagram](docs/architecture.html) | Interactive system architecture |
| [ADR 001 — FastAPI over Flask](docs/adr/adr-001-fastapi-over-flask.md) | Framework decision |
| [ADR 002 — Terraform over Bicep](docs/adr/adr-002-terraform-over-bicep.md) | IaC decision |
| [ADR 003 — Container Apps over AKS](docs/adr/adr-003-aks-over-container-apps.md) | Deployment decision |
| [ADR 004 — PostgreSQL over CosmosDB](docs/adr/adr-004-postgresql-over-cosmosdb.md) | Database decision |

---

## License

MIT — free to use, modify, and distribute.

---

<div align="center">

Built by [Farhan Shahriyar](https://linkedin.com/in/farhanshahriyar) · Hamburg, Germany  
MSc Data Science, TU Hamburg · Werkstudent AI Governance, Nordex Group

*If this platform is useful to your organisation, a ⭐ on GitHub helps others find it.*

<a href="https://www.buymeacoffee.com/farhanshahriyar" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 40px !important;width: 145px !important;" ></a>

</div>
