# ADR 003 — Azure Kubernetes Service over Azure Container Apps

**Date:** May 2026
**Status:** Accepted
**Author:** Farhan Shahriyar

---

## Context

The platform consists of six microservices that need to be
orchestrated, scaled, and managed in production. A container
orchestration solution was needed on Azure.

Two options were evaluated: Azure Kubernetes Service (AKS)
and Azure Container Apps.

---

## Options Considered

**Azure Kubernetes Service (AKS)**
Fully managed Kubernetes on Azure. Complete control over
cluster configuration. Industry standard for enterprise
container orchestration. Requires more configuration but
offers full flexibility. Kubernetes skills are universally
transferable across all cloud providers.

**Azure Container Apps**
Serverless container platform built on top of Kubernetes.
Simpler to configure than AKS. Less control over underlying
infrastructure. Good for simple microservices but limited
for complex networking requirements.

---

## Decision

**Azure Kubernetes Service (AKS)** was selected.

---

## Reasons

- Kubernetes is the universal standard for container
  orchestration — AKS skills transfer directly to AWS EKS,
  Google GKE, and on-premise clusters
- AKS provides full control over networking, which is
  required for the VNet integration and private subnet
  architecture defined in the threat model
- Horizontal Pod Autoscaling (HPA) in AKS allows precise
  control over scaling behaviour under load
- Azure Container Apps abstracts away too much of the
  infrastructure — this project is explicitly designed to
  teach enterprise-grade infrastructure skills
- AKS is standard in enterprise AI deployments — directly
  relevant to target DevSecOps and AI Governance roles

---

## Trade-offs Accepted

- AKS requires more configuration and Kubernetes knowledge
  than Container Apps
- AKS clusters have a higher baseline cost than serverless
  Container Apps
- Kubernetes adds operational complexity — this is accepted
  as a deliberate learning investment

---

## Consequences

All microservices will be deployed as Kubernetes pods on AKS.
Kubernetes manifests will be maintained in the kubernetes/
directory. HPA will be configured for all services.
Cluster access will be managed via Azure RBAC.