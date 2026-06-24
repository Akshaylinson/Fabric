# API Contracts

## Gateway

- `GET /api/health`
- `GET /api/v1/status`

## Auth Service

- `POST /api/auth/login`
- `POST /api/auth/otp/request`
- `GET /api/auth/me`
- `GET /api/health`

## Business Service

- `GET /api/customers`
- `POST /api/customers`
- `GET /api/templates`
- `POST /api/templates`
- `GET /api/fabrics`
- `GET /api/orders`
- `GET /api/audit-logs`
- `GET /api/health`

## Orchestrator Service

- `GET /health`
- `POST /jobs`
- `GET /jobs/{job_id}`
- `GET /queues`

## Template Service

- `GET /health`
- `POST /templates/from-images`

## Fabric Service

- `GET /health`
- `POST /fabric/render`

## Try-On Service

- `GET /health`
- `POST /tryon/render`
