# ADR 004 — PostgreSQL over Azure CosmosDB

**Date:** May 2026
**Status:** Accepted
**Author:** Farhan Shahriyar

---

## Context

The platform requires a database to store compliance
assessment history, user inputs, and audit logs. A database
solution on Azure was needed.

Two options were evaluated: PostgreSQL Flexible Server
on Azure and Azure CosmosDB.

---

## Options Considered

**PostgreSQL Flexible Server on Azure**
Fully managed open source relational database. ACID
compliant. Structured data with enforced schema. Standard
SQL. Widely used in enterprise applications. Open source
with no vendor lock-in beyond the managed service.

**Azure CosmosDB**
Microsoft's globally distributed NoSQL database. Multiple
APIs including MongoDB and Cassandra. Designed for massive
scale and global distribution. Proprietary service with
vendor lock-in. Higher cost at low usage levels.

---

## Decision

**PostgreSQL Flexible Server** was selected.

---

## Reasons

- Compliance assessment data is structured and relational —
  each assessment links to a user, a risk tier, a DPIA
  report, and an audit log entry. Relational data belongs
  in a relational database
- Audit logs require ACID compliance — every assessment
  must be recorded completely or not at all. PostgreSQL
  guarantees this. CosmosDB's eventual consistency model
  is not appropriate for audit data
- PostgreSQL is open source — no vendor lock-in beyond
  the managed service layer
- Standard SQL means any developer can query the database
  without learning a proprietary query language
- PostgreSQL is the most widely used open source database
  in enterprise — a standard skill for Data Governance
  and AI Compliance roles
- Significantly lower cost than CosmosDB at the usage
  levels expected for this platform

---

## Trade-offs Accepted

- PostgreSQL requires schema design upfront —
  migrations must be managed carefully
- No built-in global distribution — acceptable since
  EU data residency requires data to stay in EU regions
  anyway
- Vertical scaling has limits — acceptable given expected
  platform usage

---

## Consequences

PostgreSQL Flexible Server will be deployed in the Data
Layer private subnet. Schema migrations will be managed
using Alembic. All connections will use service accounts
with credentials stored in Azure Key Vault. Data encrypted
at rest using Azure managed keys.