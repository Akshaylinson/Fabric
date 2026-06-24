# Project: AI-Powered Textile Visualization Platform

## Objective

Build a production-grade, Dockerized, microservices-based AI platform for textile and tailoring businesses.

The platform enables textile shop staff and factory personnel to:

1. Upload new garment designs created by designers.
2. Automatically convert garment images into reusable AI-ready garment templates.
3. Allow customers to select fabrics and combine them with garment templates.
4. Generate realistic garment renders using the selected fabric.
5. Upload customer photos and generate realistic virtual try-on previews showing the customer wearing the selected garment made from the chosen fabric.

The system must be modular, scalable, containerized, and designed for future AI model upgrades.

---

# Core Business Flow

## Workflow 1 — Garment Template Creation

Performed by:

* Designers
* Factory Managers
* Admins

### Process

1. User uploads one or more images of a newly designed garment.

Examples:

* Front image
* Back image
* Side image

2. AI analyzes the garment and extracts:

* Garment type
* Collar type
* Sleeve type
* Fit type
* Length
* Pockets
* Buttons
* Structural characteristics
* Style description

3. System generates a reusable Template Package.

### Template Package must contain:

* Template ID
* Template name
* Preview image
* Segmentation masks
* Metadata JSON
* AI-generated textual description
* Embeddings vector (future use)
* Created timestamp
* Creator information

4. Template Package is permanently stored.

New templates must automatically become available in customer-facing workflows.

---

# Workflow 2 — Fabric Mapping Engine

Performed by:

* Sales Staff
* Store Managers

### Process

1. Customer selects a fabric.

2. User selects a previously created garment template.

3. System applies the fabric texture, pattern, and color onto the selected garment template.

4. System generates a rendered garment image.

Important:

The structure of the garment must remain unchanged.

Only the fabric appearance changes.

Output:

A realistic garment image using the selected fabric while preserving the original garment design.

---

# Workflow 3 — Customer Virtual Try-On

Performed by:

* Sales Staff

### Process

1. Staff uploads customer photograph.

2. Staff selects a rendered garment generated in Workflow 2.

3. AI generates a realistic preview of the customer wearing the garment.

Requirements:

* Preserve customer face.
* Preserve customer body shape.
* Preserve garment structure.
* Preserve fabric appearance.
* Produce realistic output.

Output:

Final customer preview image.

---

# Non-Functional Requirements

The system must be:

* Fully Dockerized.
* Built as independent microservices.
* API-first architecture.
* Production-ready.
* Horizontally scalable.
* Extensible for future AI models.
* Easy to maintain.
* Easy to replace AI models without affecting business logic.

---

# Architecture

## Client Layer

Flutter mobile application.

Future:

* Web admin dashboard.

---

# Backend Microservices

## API Gateway Service

Responsibilities:

* Single entry point.
* Authentication validation.
* Rate limiting.
* Request routing.
* Logging.

Technology:

NestJS.

---

## Authentication Service

Responsibilities:

* Login.
* JWT authentication.
* Role management.
* OTP.
* Session management.

Roles:

* Admin
* Designer
* Store Manager
* Sales Staff

Technology:

NestJS + PostgreSQL + Redis.

---

## Business Service

Responsibilities:

* Customers.
* Orders.
* Templates metadata.
* Generated image records.
* Staff management.
* Fabric catalog.
* Audit logs.

Technology:

NestJS + PostgreSQL.

---

## AI Orchestrator Service

Responsibilities:

* Workflow orchestration.
* AI job creation.
* Queue handling.
* Retry mechanisms.
* Status tracking.
* Event management.

Technology:

Python FastAPI + Celery + Redis.

This service coordinates all AI workflows.

---

## Template Service

Workflow 1.

Responsibilities:

* Garment image ingestion.
* Segmentation.
* Metadata extraction.
* Template package generation.

Technology:

Python FastAPI.

Initial implementation:

Create AI adapters only.

Actual AI models will be integrated later.

Provide interfaces:

* SegmentationAdapter
* MetadataAdapter
* EmbeddingAdapter

Use mock implementations initially.

---

## Fabric Service

Workflow 2.

Responsibilities:

* Receive fabric image.
* Receive template package.
* Generate rendered garment.

Technology:

Python FastAPI.

Implement adapter pattern.

Interfaces:

* FabricTransferAdapter
* TextureMappingAdapter

Use mock image generation during initial build.

---

## Try-On Service

Workflow 3.

Responsibilities:

* Receive customer image.
* Receive garment image.
* Generate final try-on image.

Technology:

Python FastAPI.

Implement adapter pattern.

Interfaces:

* HumanParsingAdapter
* PoseAdapter
* TryOnAdapter

Use mock generation initially.

---

# Shared Infrastructure

## PostgreSQL

Stores:

* Users
* Customers
* Templates metadata
* Orders
* Job records
* Audit logs

---

## Redis

Used for:

* Queues
* Caching
* Sessions
* Job status

---

## MinIO

Local object storage.

Stores:

* Customer images
* Fabric images
* Template images
* Segmentation masks
* Generated outputs

Production storage can later be replaced by Cloudflare R2 or AWS S3.

---

# Internal Communication

Use REST APIs between services.

Use Redis queues for asynchronous jobs.

Do not allow direct database access across services.

Every service owns its own domain logic.

---

# Repository Structure

textile-ai-platform/

* docker-compose.yml
* .env
* gateway/
* auth-service/
* business-service/
* orchestrator-service/
* template-service/
* fabric-service/
* tryon-service/
* shared/
* storage/
* monitoring/
* docs/

---

# Containerization

Every service must have:

* Dockerfile
* Environment configuration
* Health endpoint
* Structured logging
* OpenAPI documentation

All services must start with:

docker compose up --build

---

# Development Rules

1. Use clean architecture.
2. Use dependency injection.
3. Use repository pattern.
4. Use service layer abstraction.
5. Use adapter pattern for AI integrations.
6. Write modular code.
7. Expose OpenAPI/Swagger documentation.
8. Add health check endpoints.
9. Add centralized logging.
10. Add error handling middleware.
11. Add request validation.
12. Add asynchronous processing.
13. Make AI components replaceable.

---

# Deliverables

Build the entire project skeleton including:

* Folder structure.
* Docker setup.
* All services.
* API contracts.
* Database schemas.
* Queue setup.
* Storage integration.
* Swagger documentation.
* Health checks.
* Shared libraries.
* Example endpoints.
* Mock AI implementations.

The objective of this phase is to deliver a complete, runnable platform foundation ready for future AI model integration.
