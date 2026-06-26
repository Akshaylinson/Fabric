# Textile AI Platform

Production-grade monorepo scaffold for an AI-powered textile visualization platform.

## Services

- `gateway`: NestJS API gateway
- `auth-service`: NestJS authentication and role management
- `business-service`: NestJS business domain APIs
- `orchestrator-service`: FastAPI orchestration and job tracking
- `template-service`: FastAPI garment template creation
- `fabric-service`: FastAPI fabric mapping and OpenRouter FLUX rendering
- `tryon-service`: FastAPI API-driven workflow 3 virtual try-on rendering
- `admin-dashboard`: Next.js internal admin and QA dashboard

## Run

```bash
docker compose up --build
```

## Ports

- Gateway: `http://localhost:3000`
- Auth: `http://localhost:3001`
- Business: `http://localhost:3002`
- Orchestrator: `http://localhost:8000`
- Template: `http://localhost:8001`
- Fabric: `http://localhost:8002`
- Try-on: `http://localhost:8003`
- Admin dashboard: `http://localhost:3005`
- MinIO console: `http://localhost:9001`
- Prometheus: `http://localhost:9090`

## Notes

- AI integrations are service-backed and configured through environment variables.
- Workflow 3 now uses the API-driven try-on service instead of a local VTON model stack.
- Services communicate over REST and Redis-backed async workflows.
- Each service includes a health route and OpenAPI docs.
