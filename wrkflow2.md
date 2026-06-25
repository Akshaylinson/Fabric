# Workflow 2 Implementation Plan

## Fabric Mapping & Garment Rendering Service

Version: 1.0

---

# 1. Implementation Objective

Build a CPU-only service capable of:

1. Receiving a garment template generated from Workflow 1.
2. Receiving a customer-selected fabric image.
3. Applying the fabric onto the garment template.
4. Preserving garment structure exactly.
5. Producing a rendered garment image suitable for Virtual Try-On.

Target priorities:

1. Structural consistency.
2. Rendering speed.
3. Low infrastructure cost.
4. Maintainability.
5. Future AI upgrade compatibility.

---

# 2. High-Level Architecture

```text
Client/Admin UI
        |
        v
FastAPI API Layer
        |
        v
Workflow Orchestrator
        |
        +-----------------------+
        |                       |
        v                       v
Fabric Processing         Template Loader
        |                       |
        +-----------+-----------+
                    |
                    v
Texture Mapping Engine
                    |
                    v
Post Processing
                    |
                    v
Storage Layer
                    |
                    v
Database
```

---

# 3. Project Folder Structure

```text
workflow2/

app/
│
├── api/
│   ├── routes/
│   │   └── render.py
│   │
│   └── schemas/
│
├── services/
│   ├── validation_service.py
│   ├── segmentation_service.py
│   ├── texture_service.py
│   ├── template_service.py
│   ├── mapping_service.py
│   ├── postprocess_service.py
│   ├── storage_service.py
│   └── render_service.py
│
├── core/
│   ├── config.py
│   └── exceptions.py
│
├── utils/
│   ├── image_utils.py
│   ├── opencv_utils.py
│   └── file_utils.py
│
├── models/
│
├── database/
│
├── workers/
│
└── main.py

storage/
├── uploads/
├── textures/
├── renders/
└── temp/
```

---

# 4. Development Phases

# Phase 1 — Foundation Setup

Duration:
2 Days

Tasks:

* Create service repository.
* Setup FastAPI project.
* Setup environment variables.
* Setup logging.
* Setup storage directories.
* Setup database connection.
* Setup Docker environment (optional).

Deliverables:

* Running FastAPI service.
* Health check endpoint.

API:

```text
GET /health
```

---

# Phase 2 — Fabric Upload Service

Duration:
1 Day

Features:

* Upload fabric image.
* Validate file type.
* Generate UUID.
* Save uploaded file.

Accepted Formats:

* JPG
* PNG
* WEBP

Validation:

* Maximum file size.
* Mime type validation.

Endpoints:

```text
POST /fabric/upload
```

Response:

```json
{
  "fabric_id":"FAB_001",
  "path":"uploads/fabric.jpg"
}
```

Deliverables:

* Upload API working.

---

# Phase 3 — Fabric Validation Service

Duration:
2 Days

Purpose:

Reject unusable images.

Implementation:

OpenCV-based validation.

Checks:

## Resolution Check

Minimum:

1024x1024

## Blur Detection

Method:

Laplacian variance.

Threshold:

Configurable.

## Brightness Detection

Reject:

Very dark images.

## Contrast Detection

Reject:

Extremely low contrast.

## Corrupted Image Check

Verify image decoding.

Output:

```json
{
  "valid": true,
  "errors":[]
}
```

Deliverables:

* Automatic image validation.

---

# Phase 4 — Fabric Background Removal

Duration:
2 Days

Library:

rembg

Tasks:

* Remove background.
* Generate transparent PNG.

Input:

```text
fabric.jpg
```

Output:

```text
fabric_clean.png
```

Deliverables:

* Transparent fabric image generation.

---

# Phase 5 — Texture Preparation Engine

Duration:
4 Days

Purpose:

Generate clean texture.

Tasks:

## Crop fabric region.

## Normalize colors.

## Reduce shadows.

## Resize texture.

## Generate seamless tile.

Methods:

OpenCV.

Functions:

* CLAHE
* Histogram equalization
* Perspective transform

Outputs:

```text
texture.png
```

Deliverables:

* Clean normalized texture.

---

# Phase 6 — Template Loader

Duration:
2 Days

Input:

Workflow 1 template package.

Load:

```text
preview.png
mask.png
metadata.json
```

Validate:

* Files exist.
* Mask integrity.
* Template status.

Deliverables:

* Template package loader.

---

# Phase 7 — Texture Mapping Engine (Core)

Duration:
7 Days

Purpose:

Apply fabric onto garment.

Pipeline:

```text
Load Template
↓
Load Texture
↓
Resize Texture
↓
Tile Texture
↓
Apply Garment Mask
↓
Blend With Garment
↓
Generate Render
```

Implementation:

## Step 1

Load garment mask.

## Step 2

Generate repeated texture tile.

## Step 3

Resize texture to garment area.

## Step 4

Apply mask.

## Step 5

Preserve garment details.

Techniques:

* Alpha masking
* Seamless cloning
* Weighted blending

Deliverables:

* First garment render.

---

# Phase 8 — Post Processing

Duration:
3 Days

Tasks:

* Edge smoothing.
* Sharpening.
* Contrast enhancement.
* Color correction.

OpenCV Techniques:

* Bilateral filter.
* Gaussian blur.
* Unsharp mask.

Deliverables:

* Improved realism.

---

# Phase 9 — Storage Layer

Duration:
2 Days

Storage Structure:

```text
renders/
    render_id/
        rendered.png
        texture.png
        metadata.json
        logs.json
```

Store:

* Render image.
* Texture image.
* Processing metadata.

Deliverables:

* Persistent storage.

---

# Phase 10 — Render Orchestration Service

Duration:
3 Days

Purpose:

Coordinate entire workflow.

Pipeline:

```text
Validate Fabric
↓
Remove Background
↓
Prepare Texture
↓
Load Template
↓
Map Texture
↓
Post Process
↓
Store Output
```

Output:

```json
{
    "render_id":"REN_001",
    "status":"completed"
}
```

Deliverables:

* End-to-end pipeline.

---

# Phase 11 — API Layer

Duration:
2 Days

Endpoints:

```text
POST /fabric/render

GET /fabric/render/{id}

GET /fabric/renders

DELETE /fabric/render/{id}
```

Deliverables:

* Public APIs.

---

# Phase 12 — Admin Testing UI

Duration:
3 Days

Features:

* Select template.
* Upload fabric.
* Generate render.
* View render history.
* Download render.

Pages:

```text
Templates
Fabric Upload
Render Preview
Render History
```

Deliverables:

* Internal testing portal.

---

# Phase 13 — Testing

Duration:
5 Days

Testing Types:

## Unit Tests

Each service independently.

## Integration Tests

Entire pipeline.

## Performance Tests

Render timing.

## Edge Cases

* Blurry fabric.
* Large images.
* Invalid mask.
* Empty uploads.

Target:

95% successful renders.

---

# 5. Database Tables

## renders

```text
id
template_id
fabric_id
storage_path
status
created_at
processing_duration
metadata
```

---

# 6. Milestones

Milestone 1

Foundation completed.

Milestone 2

Fabric processing completed.

Milestone 3

Template loading completed.

Milestone 4

Texture mapping engine completed.

Milestone 5

End-to-end rendering completed.

Milestone 6

Testing completed.

Milestone 7

Production deployment.

---

# 7. Estimated Timeline

| Phase               | Duration |
| ------------------- | -------- |
| Foundation          | 2 Days   |
| Upload              | 1 Day    |
| Validation          | 2 Days   |
| Background Removal  | 2 Days   |
| Texture Preparation | 4 Days   |
| Template Loader     | 2 Days   |
| Mapping Engine      | 7 Days   |
| Post Processing     | 3 Days   |
| Storage             | 2 Days   |
| Orchestration       | 3 Days   |
| API Layer           | 2 Days   |
| Admin UI            | 3 Days   |
| Testing             | 5 Days   |

Total:

Approximately 5 Weeks.

---

# 8. MVP Technology Stack

Backend:
FastAPI

Image Processing:
OpenCV

Background Removal:
rembg

Image Utilities:
Pillow

Numerical Processing:
NumPy

Storage:
MinIO or Local Filesystem

Database:
PostgreSQL

Testing:
Pytest

Deployment:
Docker + Nginx

Server Requirement:

8 CPU cores
16 GB RAM
100 GB SSD

```
```
