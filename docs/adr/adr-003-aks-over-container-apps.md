# ADR 003 — Azure Container Apps over AKS for Initial Deployment

**Date:** May 2026
**Status:** Accepted — Revised
**Author:** Farhan Shahriyar

---

## Context

The platform needed a container hosting solution on Azure.
Two options were evaluated: Azure Kubernetes Service (AKS)
and Azure Container Apps.

The original ADR selected AKS. After evaluating actual
deployment constraints — Azure for Students subscription
limits, time-to-production requirements, and the platform's
current scale — the decision was revised to Azure Container
Apps for the initial production deployment.

---

## Options Considered

**Azure Kubernetes Service (AKS)**
Fully managed Kubernetes. Full control over networking,
scaling, and cluster configuration. Transferable skills
across AWS EKS and Google GKE. Higher operational overhead
and baseline cost. Requires VNet, node pool, and cluster
configuration before deploying a single container.

**Azure Container Apps**
Serverless container platform built on Kubernetes internally.
Significantly simpler deployment model. Built-in HTTPS,
ingress, and scaling. No cluster management required.
Lower cost for student-tier subscriptions. Kubernetes
manifests prepared for future migration to AKS.

---

## Decision

**Azure Container Apps** for current production deployment,
with Kubernetes manifests maintained in `k8s/` for
future AKS migration.

---

## Reasons

- Azure for Students subscription has resource constraints
  that make AKS cluster provisioning impractical
- Container Apps provides production-grade HTTPS, autoscaling,
  and zero-downtime deployments without cluster management
- The platform serves as a portfolio project where shipping
  a working live system demonstrates more than undeployed
  Kubernetes configuration
- All three services (API, Prometheus, Grafana) deployed
  successfully to Container Apps with full observability
- Kubernetes manifests in `k8s/` provide a clear migration
  path to AKS when scaling requirements demand it

---

## Trade-offs Accepted

- Less infrastructure control than AKS
- Container Apps abstracts away Kubernetes internals
- Migration to AKS required when VNet isolation or
  custom node configuration becomes necessary

---

## Consequences

API, Prometheus, and Grafana run as separate Container Apps
in the `rg-eu-ai-governance` resource group. CI/CD pipeline
automatically deploys via `az containerapp update` on every
push to main. Kubernetes manifests in `k8s/` remain
maintained for future AKS migration.
