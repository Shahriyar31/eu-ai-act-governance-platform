# ADR 001 — FastAPI over Flask and Django

**Date:** May 2026
**Status:** Accepted
**Author:** Farhan Shahriyar

---

## Context

The governance platform requires a REST API layer that handles
compliance assessment requests, routes them to the correct
microservice, and returns results to the client. A Python web
framework was needed for this purpose.

Three options were evaluated: FastAPI, Flask, and Django.

---

## Options Considered

**FastAPI**
Modern Python framework built for APIs. Automatic OpenAPI
documentation generation. Built-in request validation using
Pydantic. Async support out of the box. Very high performance.

**Flask**
Lightweight and flexible. Large ecosystem. Simple to learn.
No built-in validation or documentation generation. Requires
additional libraries for async support.

**Django**
Full-featured framework with ORM, admin panel, and auth built
in. Too heavy for a microservices API. Designed for monolithic
web applications, not lightweight REST APIs.

---

## Decision

**FastAPI** was selected.

---

## Reasons

- Automatic Swagger UI documentation generated at /docs —
  essential for an open source project where contributors
  need to understand the API without reading code
- Built-in request validation via Pydantic catches malformed
  compliance assessment inputs before they reach business logic
- Native async support means multiple compliance assessments
  can be processed concurrently without blocking
- Performance benchmarks show FastAPI is significantly faster
  than Flask for API workloads
- Type hints throughout the codebase improve code readability
  and catch errors at development time

---

## Trade-offs Accepted

- FastAPI has a smaller ecosystem than Flask
- Slightly steeper learning curve than Flask for beginners
- Pydantic v2 has breaking changes from v1 — version must
  be pinned carefully

---

## Consequences

All microservices will be built using FastAPI. Each service
will expose automatic Swagger documentation. Request
validation will be handled by Pydantic models throughout.