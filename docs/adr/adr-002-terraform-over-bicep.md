# ADR 002 — Terraform over Azure Bicep

**Date:** May 2026
**Status:** Accepted
**Author:** Farhan Shahriyar

---

## Context

All Azure infrastructure for this platform must be defined
as code. No manual configuration in the Azure portal is
permitted. An Infrastructure as Code tool was needed.

Two options were evaluated: Terraform and Azure Bicep.

---

## Options Considered

**Terraform**
Open source IaC tool by HashiCorp. Provider ecosystem covers
every major cloud provider. HCL syntax is readable and
well-documented. State management built in. Multi-cloud
capable. Industry standard across enterprises globally.

**Azure Bicep**
Microsoft's native IaC language for Azure. Simpler syntax
than ARM templates. Azure-only. Deep integration with Azure
tooling. No state management — relies on Azure's own
deployment history.

---

## Decision

**Terraform** was selected.

---

## Reasons

- Terraform is cloud-agnostic — skills learned here apply
  to AWS, GCP, and any other provider. Bicep locks you
  into Azure exclusively
- Terraform is the industry standard for IaC in enterprise
  DevSecOps and AI Governance roles — the primary target
  career path for this project
- Terraform state management provides a clear picture of
  exactly what infrastructure exists at any point
- Larger community means more modules, examples, and
  troubleshooting resources available
- Terraform Provider for Azure is mature and covers all
  required Azure services including AKS, ACR, Key Vault,
  and PostgreSQL

---

## Trade-offs Accepted

- Terraform requires state file management — state will be
  stored in Azure Blob Storage with state locking
- HCL syntax has a learning curve compared to Bicep's
  closer alignment to Azure portal concepts
- HashiCorp changed Terraform's licence to BSL in 2023 —
  OpenTofu exists as the open source fork if needed

---

## Consequences

All Azure infrastructure will be provisioned via Terraform.
State will be stored remotely in Azure Blob Storage.
No manual changes to Azure resources are permitted —
all changes go through Terraform and the CI/CD pipeline.