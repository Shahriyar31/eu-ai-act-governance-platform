# Threat Model — EU AI Act Governance Platform

**Version:** 1.0  
**Date:** May 2026  
**Author:** Farhan Shahriyar  
**Methodology:** STRIDE  
**Tool:** OWASP Threat Dragon v2.6.2  
**Status:** Active  

---

## 1. Overview

This document summarises the STRIDE-based threat model for the
EU AI Act Governance Platform. The full machine-readable threat
model is available in `threat-model.json` and was produced using
OWASP Threat Dragon.

Threat modelling was conducted before any code was written —
identifying attack surfaces, trust boundaries, and mitigations
at the design stage rather than after deployment.

---

## 2. Trust Boundaries

Three trust boundaries were identified:

**Internet Boundary**
Separates untrusted external actors from the platform.
All traffic crossing this boundary must be authenticated
and encrypted.

**Internal Network Boundary**
Separates the API Gateway and microservices from the
public internet. Components inside this boundary
communicate over private Azure VNet only.

**Data Layer Boundary**
Separates all data storage from the application layer.
No data store is directly accessible from the internet.
All access requires service accounts with least privilege.

---

## 3. Threat Register

| # | Component | Threat | STRIDE Category | Severity | Mitigation |
|---|---|---|---|---|---|
| 1 | API Gateway | Unauthenticated API Access | Spoofing | High | JWT token validation via Azure API Management |
| 2 | API Gateway | API Flooding — Denial of Service | Denial of Service | High | Rate limiting in APIM. Kubernetes HPA auto-scaling |
| 3 | EU AI Act Classifier | Classification Result Manipulation | Tampering | Critical | TLS encryption for all internal communication. Results signed before transmission |
| 4 | DPIA Generator | Sensitive Data Exposure | Information Disclosure | High | DPIA reports encrypted in Azure Blob Storage. RBAC access control. TLS in transit |
| 5 | OWASP LLM Checker | Manipulated Assessment Results | Tampering | High | Results validated and signed. Audit log records all outputs |
| 6 | PDF Generator | Report Interception | Information Disclosure | Medium | All transfers over TLS. Time-limited download links from Azure Blob Storage |
| 7 | RAG Assistant | Prompt Injection Attack | Tampering | Critical | Input validation and sanitisation. LLM guardrails. Output filtering |
| 8 | PostgreSQL | Database Breach | Information Disclosure | Critical | Private subnet — no public access. Azure Key Vault credentials. Encrypted at rest |
| 9 | Azure Key Vault | Secret Theft | Elevation of Privilege | Critical | Managed Identity only — no passwords. RBAC with least privilege. Full audit logging |
| 10 | GitHub Actions Pipeline | Supply Chain Attack | Tampering | High | Actions pinned to commit SHA. SAST and SCA on every build. Dependency review enabled |

---

## 4. Critical Threats Summary

Four threats were classified as **Critical** severity:

**Prompt Injection on RAG Assistant**
The most unique threat to this platform. LLM-based systems
are vulnerable to carefully crafted inputs that bypass
safety instructions. Mitigated through input validation,
guardrails, and output filtering.

**Classification Result Manipulation**
If a High risk EU AI Act classification is tampered with
in transit, an organisation could deploy a non-compliant
AI system believing it is safe. Mitigated through TLS
and result signing.

**Database Breach**
All compliance assessments and audit logs stored in
PostgreSQL. A breach would expose sensitive organisational
data. Mitigated through private subnet deployment and
encryption at rest.

**Secret Theft from Azure Key Vault**
If encryption keys and API credentials are stolen, an
attacker gains full access to all platform components.
Mitigated through Managed Identity — no passwords exist
to steal.

---

## 5. Security Principles Applied

- **Defence in depth** — multiple security layers, no single point of failure
- **Least privilege** — every service has minimum required permissions only
- **Zero trust** — all traffic authenticated regardless of network location
- **Shift left security** — threats identified before code was written
- **Secrets management** — no credentials in code or environment variables

---

## 6. Residual Risks

The following risks remain and will be addressed during
implementation:

- OWASP ZAP DAST scanning will be run against staging
  environment in Sprint 2 to identify runtime vulnerabilities
- Penetration testing recommended before any public release
- Threat model should be reviewed and updated after each
  major sprint as new components are added

---

## 7. Running OWASP Threat Dragon Locally

This threat model was produced using OWASP Threat Dragon v2.6.2
running locally via Docker Engine on Ubuntu.

### Prerequisites

- Docker Engine installed and running
- Port 8080 available on your machine

### Installation

**Step 1 — Pull the official image:**

```bash
docker pull threatdragon/owasp-threat-dragon:stable
```

**Step 2 — Create a local directory and .env file:**

```bash
mkdir ~/threat-dragon-local
cd ~/threat-dragon-local
nano .env
```

**Step 3 — Add the following to your .env file:**

```
NODE_ENV=development
SERVER_API_PROTOCOL=http
ENCRYPTION_JWT_SIGNING_KEY=localdevelopmentjwtkey12345678
ENCRYPTION_JWT_REFRESH_SIGNING_KEY=localdevelopmentrefreshkey12345
ENCRYPTION_KEYS=[{"isPrimary":true,"id":0,"value":"11223344556677889900aabbccddeeff"}]
```

> Note: These are local development keys only.
> For production generate real keys using openssl rand -hex 16

**Step 4 — Run the container:**

```bash
docker run -it --rm -p 8080:3000 \
  -v $(pwd)/.env:/app/.env \
  threatdragon/owasp-threat-dragon:stable
```

**Step 5 — Open in browser:**
```http://localhost:8080```    

Click Login to Local Session to begin.

---

### Known Errors and Fixes

**Error 1 — docker-credential-desktop not found**

error getting credentials - err: exec:
"docker-credential-desktop": executable file not found in $PATH 
Cause: Leftover Docker Desktop configuration after
switching to Docker Engine.

Fix:

```bash
cat > ~/.docker/config.json << 'EOF'
{}
EOF

export DOCKER_HOST=unix:///run/docker.sock
echo 'export DOCKER_HOST=unix:///run/docker.sock' >> ~/.zshrc
source ~/.zshrc
```

---

**Error 2 — ENCRYPTION_KEYS is a required property**

ENCRYPTION_KEYS is a required property,
Threat Dragon server cannot start without it.

unexpected EOF

Cause: Docker Desktop crashed mid-download,
corrupting the image layers.

Fix: Close Docker Desktop completely. Use
Docker Engine directly instead:

```bash
sudo apt install docker.io
sudo systemctl start docker
sudo usermod -aG docker $USER
```

Log out and log back in, then pull again.

---

**Error 4 — failed to connect to docker API**

failed to connect to the docker API at
unix:///home/user/.docker/desktop/docker.sock

Cause: Docker is looking for Docker Desktop socket
which no longer exists.

Fix:

```bash
export DOCKER_HOST=unix:///run/docker.sock
```

---

### Reopening the Threat Model

To view or edit the threat model again:

1. Start the container using Step 4 above
2. Open http://localhost:8080
3. Click Open an existing threat model
4. Select docs/threat-model.json from this repository

---

*Threat model produced using OWASP Threat Dragon v2.6.2
running locally via Docker. Full JSON export available
at docs/threat-model.json.*