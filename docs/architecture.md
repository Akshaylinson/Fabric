# Architecture Overview

## Boundaries

- Gateway handles routing, auth validation, rate limiting, and logging.
- Auth owns identity, roles, OTP, and sessions.
- Business owns customers, orders, templates metadata, fabrics, jobs, and audit logs.
- Orchestrator owns workflow coordination, queues, retries, and status tracking.
- Template, Fabric, and Try-On services own their workflow-specific AI adapters.

## Storage

- PostgreSQL: transactional records
- Redis: queues, sessions, job state
- MinIO: object storage for source images and outputs

## Replaceable AI

Each AI workflow is hidden behind adapter interfaces so the mock implementation can be swapped for a real model without changing service contracts.

