# Workflow 2 Implementation Plan

## Final-Quality Fabric Mapping & Product Render Service

Version: 2.0

---

# 1. Implementation Objective

Build a service that generates a final-quality garment product render from:

1. A garment template generated in Workflow 1.
2. A customer-selected fabric image.
3. Template metadata describing garment parts, trims, shadows, seams, buttons, pockets, collars, sleeves, and protected regions.

Workflow 2 must produce a reference-style product render, not a flat fabric overlay. The target quality is the side-by-side reference image: the rendered output must look like the same garment photographed as a clean catalog/product image with the selected fabric applied realistically.

The output must be suitable as the garment input for Workflow 3 virtual try-on.

---

# 2. Final-Quality Render Target

The render must preserve exactly:

* Garment silhouette and crop.
* Shoulder slope, sleeve length, and body proportions.
* Collar shape, collar border, and neck opening.
* Front placket width and alignment.
* Button count, size, spacing, color, and sharpness.
* Pocket position, pocket shape, and pocket trim.
* Vertical trim/piping positions and spacing.
* Hem/rib detail.
* Brand label and small hardware details.
* Background style and camera angle.

The render may change only:

* Fabric color.
* Fabric pattern.
* Fabric weave or surface texture.
* Fabric repeat scale when needed for realism.

The render must not:

* Redesign the garment.
* Move buttons, pocket, placket, trims, collar, sleeves, or hem.
* Recolor protected trims or piping unless explicitly requested.
* Blur buttons, labels, trims, or garment edges.
* Look like a simple color fill or pasted texture.

Reference-quality behavior:

```text
Template garment
    +
Selected fabric
    +
Template structure maps
    +
Lighting/detail preservation
    =
Catalog-ready rendered garment
```

---

# 3. High-Level Architecture

```text
Client/Admin UI
        |
        v
FastAPI API Layer
        |
        v
Render Orchestrator
        |
        +------------------------+
        |                        |
        v                        v
Fabric Processing          Template Package Loader
        |                        |
        v                        v
Texture Preparation        Garment Structure Maps
        |                        |
        +-----------+------------+
                    |
                    v
Part-Aware Texture Mapping Engine
                    |
                    v
Lighting & Detail Recomposition
                    |
                    v
Trim/Button/Label Restoration
                    |
                    v
Product Render Post Processing
                    |
                    v
Quality Validation
                    |
                    v
Storage Layer
                    |
                    v
Database
```

---

# 4. Required Template Package From Workflow 1

A single preview image and mask are not enough for final-quality rendering. Workflow 2 needs a structure-preserving template package.

Required final-quality template assets:

```text
template_package/
    preview.png
    garment_mask.png
    fabric_region_mask.png
    trim_mask.png
    button_mask.png
    label_mask.png
    collar_mask.png
    placket_mask.png
    pocket_mask.png
    sleeve_left_mask.png
    sleeve_right_mask.png
    body_left_mask.png
    body_right_mask.png
    hem_mask.png
    shadow_map.png
    highlight_map.png
    detail_map.png
    normal_hint_map.png
    displacement_hint_map.png
    uv_map.png
    metadata.json
```

Minimum acceptable final-quality assets:

* `preview.png`
* `garment_mask.png`
* `fabric_region_mask.png`
* `trim_mask.png`
* `button_mask.png`
* `shadow_map.png`
* `highlight_map.png`
* `detail_map.png`
* `metadata.json`

Recommended metadata:

```json
{
  "template_id": "TPL_001",
  "category": "shirt",
  "view": "front",
  "render_style": "catalog_product",
  "canvas": {
    "width": 1400,
    "height": 1400
  },
  "garment_parts": [
    "body_left",
    "body_right",
    "sleeve_left",
    "sleeve_right",
    "collar",
    "placket",
    "pocket",
    "hem"
  ],
  "protected_regions": [
    "trim",
    "buttons",
    "label"
  ],
  "fabric_regions": [
    "body_left",
    "body_right",
    "sleeve_left",
    "sleeve_right",
    "collar",
    "pocket"
  ],
  "quality_profile": "final"
}
```

---

# 5. Rendering Strategy

## 5.1 Deterministic Base Renderer

The base renderer should be CPU-friendly and part-aware.

Required behavior:

1. Load the template package.
2. Validate all required masks and maps.
3. Prepare the selected fabric as a seamless render texture.
4. Apply fabric separately to each garment part.
5. Warp fabric per part using UV maps or perspective transforms.
6. Preserve template shadows, highlights, folds, seams, and detail maps.
7. Restore trims, buttons, labels, and protected regions on top.
8. Post-process for catalog realism.
9. Validate output against structural quality rules.

## 5.2 Optional Production AI Refinement

For the product-render quality shown in the reference, production can support a hybrid renderer:

* Deterministic OpenCV/Pillow pipeline for structure preservation.
* Optional AI image-editing refinement for fabric realism.
* Strict editable masks limited to fabric regions.
* Automated comparison against template geometry before accepting output.

The AI refinement step should be used only after deterministic mapping creates a correct base render.

Prompt requirements:

```text
Create a realistic catalog product render of the same garment.
Preserve the exact silhouette, collar, placket, pocket, trim lines, buttons, label, sleeve shape, and hem.
Apply only the provided fabric texture to the fabric regions.
Do not redesign the garment.
Do not change trim color.
Do not move buttons, pocket, collar, placket, sleeves, or hem.
Keep the same camera angle and clean studio background.
```

Acceptance rules:

* Reject AI output if garment geometry changes.
* Reject AI output if buttons, trims, pocket, collar, or label move.
* Reject AI output if protected trims are recolored.
* Reject AI output if fabric identity changes too much.

---

# 6. Project Folder Structure

```text
workflow2/

app/
    api/
        routes/
            render.py
        schemas/
    services/
        validation_service.py
        fabric_extraction_service.py
        texture_service.py
        template_service.py
        mapping_service.py
        lighting_service.py
        protected_region_service.py
        quality_service.py
        postprocess_service.py
        storage_service.py
        render_service.py
    core/
        config.py
        exceptions.py
    utils/
        image_utils.py
        opencv_utils.py
        file_utils.py
    models/
    database/
    workers/
    main.py

storage/
    uploads/
    textures/
    renders/
    temp/
```

---

# 7. Development Phases

# Phase 1 - Foundation Setup

Duration: 2 Days

Tasks:

* Create service repository/module.
* Setup FastAPI project.
* Setup environment variables.
* Setup logging.
* Setup storage directories.
* Setup database connection.
* Setup Docker environment.
* Add render quality profiles: `draft`, `standard`, `final`.

Deliverables:

* Running FastAPI service.
* Health check endpoint.
* Render configuration loaded from environment.

API:

```text
GET /health
```

---

# Phase 2 - Fabric Upload Service

Duration: 1 Day

Features:

* Upload fabric image.
* Validate file type.
* Generate UUID.
* Save uploaded file.
* Store original image without destructive preprocessing.

Accepted formats:

* JPG
* PNG
* WEBP

Endpoint:

```text
POST /fabric/upload
```

Response:

```json
{
  "fabric_id": "FAB_001",
  "path": "uploads/fabric.jpg"
}
```

---

# Phase 3 - Fabric Validation Service

Duration: 2 Days

Purpose:

Reject unusable fabric images before render time.

Checks:

* Minimum resolution: 1024 x 1024.
* Blur detection using Laplacian variance.
* Brightness and contrast checks.
* Corrupted image check.
* Repeating pattern suitability.
* Excessive perspective distortion.
* Heavy shadow rejection.
* Watermark/text/logo detection where possible.

Output:

```json
{
  "valid": true,
  "errors": [],
  "warnings": []
}
```

---

# Phase 4 - Fabric Region Extraction

Duration: 2 Days

Purpose:

Extract the usable fabric region from the customer image.

Preferred approach:

* Crop or segment the actual fabric area.
* Remove background if the fabric is photographed as a swatch.
* Correct perspective when the fabric is photographed at an angle.
* Normalize uneven lighting.

Libraries:

* OpenCV
* Pillow
* rembg, only when background removal is needed

Outputs:

```text
fabric_clean.png
fabric_crop.png
fabric_mask.png
```

---

# Phase 5 - Texture Preparation Engine

Duration: 4 Days

Purpose:

Generate a clean, repeatable render texture from the uploaded fabric.

Tasks:

* Crop usable region.
* Correct perspective.
* Normalize exposure and color.
* Reduce shadows without removing fabric character.
* Generate seamless tile.
* Estimate texture scale.
* Preserve weave and pattern detail.
* Generate texture preview.

Methods:

* CLAHE.
* White balance correction.
* High-pass detail preservation.
* Frequency separation.
* Seamless tiling.
* Optional pattern repeat detection.

Outputs:

```text
texture.png
texture_tile.png
texture_preview.png
texture_metadata.json
```

---

# Phase 6 - Template Loader

Duration: 2 Days

Input:

Workflow 1 template package.

Load:

* Preview image.
* Garment mask.
* Fabric region masks.
* Protected region masks.
* Shadow/highlight/detail maps.
* UV or displacement hint maps.
* Metadata.

Validate:

* Required files exist.
* Masks match preview dimensions.
* Masks are binary or normalized.
* Protected regions do not overlap incorrectly.
* Template status is approved.
* Template supports requested render quality.

Deliverables:

* Template package loader.
* Template validation report.

---

# Phase 7 - Part-Aware Texture Mapping Engine

Duration: 8 Days

Purpose:

Apply fabric onto the garment while preserving structure.

Pipeline:

```text
Load Template Package
        |
Load Prepared Texture
        |
Create Per-Part Texture Tiles
        |
Warp Texture To Garment Parts
        |
Apply Fabric Region Masks
        |
Compose Base Fabric Render
        |
Reapply Shadows, Highlights, Folds, and Detail
        |
Restore Protected Regions
        |
Generate Render
```

Required implementation:

* Separate mapping for body, sleeves, collar, placket, pocket, and hem.
* Per-part texture scale and orientation.
* UV-map mapping when available.
* Perspective transform fallback when UV map is unavailable.
* Mask feathering at part boundaries.
* Seam alignment across body panels where possible.
* Trim protection so white piping remains white.
* Button and label restoration from original preview.

Deliverables:

* Structurally accurate first render.
* Per-layer debug output.

Debug outputs:

```text
debug/
    fabric_regions.png
    warped_body.png
    warped_sleeves.png
    shadow_recompose.png
    protected_restore.png
    final_compare.png
```

---

# Phase 8 - Lighting & Detail Recomposition

Duration: 4 Days

Purpose:

Make the mapped fabric look like it belongs to the garment, not pasted on top.

Required maps:

* Shadow map.
* Highlight map.
* Detail map.
* Edge map.

Techniques:

* Multiply shadows into fabric regions.
* Screen/add highlights with controlled strength.
* Reintroduce seam, fold, knit, and rib detail.
* Preserve fabric texture detail using high-frequency blending.
* Prevent shadow maps from muddying bright fabrics.

Deliverables:

* Realistic depth and garment volume.
* Visible seams, folds, and construction details.

---

# Phase 9 - Protected Region Restoration

Duration: 2 Days

Purpose:

Restore non-fabric garment components after fabric mapping.

Protected elements:

* White piping/trims.
* Buttons.
* Brand labels.
* Inner collar label.
* Stitch lines that must remain original.
* Pocket edge trim.
* Placket edge trim.

Rules:

* Protected regions are copied from the original template preview.
* Edges are feathered minimally to avoid halos.
* Protected masks override fabric regions.
* Buttons must remain circular, sharp, and aligned.

Deliverables:

* Clean trims and hardware.

---

# Phase 10 - Product Render Post Processing

Duration: 3 Days

Tasks:

* Edge smoothing.
* Anti-aliasing.
* Local sharpening.
* Contrast balancing.
* Color correction.
* Background cleanup.
* Output crop normalization.
* Optional transparent background export.

OpenCV techniques:

* Bilateral filter.
* Guided filter.
* Gaussian blur for masks only.
* Unsharp mask.
* Morphological cleanup.

Outputs:

```text
rendered.png
rendered_transparent.png
rendered_preview.jpg
```

---

# Phase 11 - Optional AI Refinement

Duration: 3 Days

Purpose:

Improve final realism while keeping deterministic structure.

This step is optional for MVP but recommended for final-quality product renders.

Input:

* Deterministic base render.
* Original template preview.
* Fabric texture.
* Strict editable mask limited to fabric regions.

Recommended providers:

* OpenAI image editing for MVP.
* Fashion-specific image API for production if higher garment fidelity is needed.

---

# Phase 12 - Quality Validation

Duration: 4 Days

Purpose:

Automatically reject poor renders.

Validation checks:

* Garment mask IoU against template: target >= 0.98.
* Protected trim mask color consistency.
* Button count and approximate button location.
* Pocket bounding box location.
* Collar region preservation.
* Placket alignment.
* Edge artifact detection.
* Output sharpness.
* Background cleanliness.
* Fabric coverage percentage.
* Structural similarity against template detail regions.

Output:

```json
{
  "passed": true,
  "score": 0.94,
  "checks": {
    "mask_iou": 0.992,
    "button_alignment": true,
    "trim_preserved": true,
    "pocket_preserved": true,
    "sharpness": 0.87
  }
}
```

Quality profiles:

```text
draft    - fast preview, relaxed validation
standard - internal approval quality
final    - catalog/product-render quality matching the reference target
```

---

# Phase 13 - Storage Layer

Duration: 2 Days

Storage structure:

```text
renders/
    render_id/
        rendered.png
        rendered_transparent.png
        rendered_preview.jpg
        texture.png
        texture_metadata.json
        quality_report.json
        metadata.json
        logs.json
        debug/
```

Store:

* Final render image.
* Prepared texture.
* Template version.
* Render configuration.
* Quality report.
* Debug layers for failed renders.

Deliverables:

* Persistent storage.
* Reproducible render records.

---

# Phase 14 - Render Orchestration Service

Duration: 3 Days

Purpose:

Coordinate the full workflow.

Pipeline:

```text
Validate Fabric
        |
Extract Fabric Region
        |
Prepare Texture
        |
Load Template Package
        |
Map Texture Per Garment Part
        |
Recompose Lighting and Detail
        |
Restore Protected Regions
        |
Post Process Product Render
        |
Optional AI Refinement
        |
Validate Quality
        |
Store Output
```

Output:

```json
{
  "render_id": "REN_001",
  "status": "completed",
  "quality_profile": "final",
  "quality_score": 0.94
}
```

---

# Phase 15 - API Layer

Duration: 2 Days

Endpoints:

```text
POST /fabric/upload
POST /fabric/render
GET /fabric/render/{id}
GET /fabric/renders
GET /fabric/render/{id}/quality
GET /fabric/render/{id}/debug
DELETE /fabric/render/{id}
```

Render request:

```json
{
  "template_id": "TPL_001",
  "fabric_id": "FAB_001",
  "quality_profile": "final",
  "use_ai_refinement": true
}
```

---

# Phase 16 - Admin Testing UI

Duration: 3 Days

Features:

* Select template.
* Upload fabric.
* Choose render quality profile.
* Generate render.
* Compare template and output side by side.
* Toggle debug layers.
* View quality report.
* Approve/reject render.
* Download render.
* View render history.

Pages:

```text
Templates
Fabric Upload
Render Preview
Quality Report
Render History
```

The preview UI should match the reference review format:

```text
Template (Original) | Rendered Output
```

---

# Phase 17 - Testing

Duration: 5 Days

Testing types:

* Unit tests for each service.
* Integration tests for full render pipeline.
* Golden-image regression tests.
* Mask integrity tests.
* Protected-region preservation tests.
* Performance tests.
* Failed-render debug artifact tests.

Edge cases:

* Blurry fabric.
* Very dark fabric.
* White fabric.
* Striped fabric.
* Small repeating pattern.
* Large floral pattern.
* Fabric with strong shadows.
* Invalid masks.
* Missing protected-region masks.
* Large upload.
* Transparent template.

Targets:

* 95% successful renders for approved templates and valid fabrics.
* Final render generated under 20 seconds without AI refinement.
* Final render generated under provider SLA with AI refinement.
* Structural validation pass rate >= 98% for approved templates.

---

# 8. Database Tables

## renders

```text
id
template_id
fabric_id
storage_path
quality_profile
quality_score
status
use_ai_refinement
provider
model
created_at
processing_duration
metadata
```

## render_quality_reports

```text
id
render_id
mask_iou
trim_preserved
button_alignment
pocket_preserved
collar_preserved
sharpness_score
background_score
overall_score
passed
errors
warnings
created_at
```

---

# 9. Milestones

Milestone 1: Foundation completed.

Milestone 2: Fabric processing completed.

Milestone 3: Template package loading completed.

Milestone 4: Part-aware texture mapping completed.

Milestone 5: Lighting/detail recomposition completed.

Milestone 6: Protected-region restoration completed.

Milestone 7: Quality validation completed.

Milestone 8: Optional AI refinement integrated.

Milestone 9: Admin review UI completed.

Milestone 10: Production deployment.

---

# 10. Estimated Timeline

| Phase | Duration |
| --- | --- |
| Foundation | 2 Days |
| Upload | 1 Day |
| Validation | 2 Days |
| Fabric Extraction | 2 Days |
| Texture Preparation | 4 Days |
| Template Loader | 2 Days |
| Part-Aware Mapping | 8 Days |
| Lighting/Detail Recomposition | 4 Days |
| Protected Restoration | 2 Days |
| Post Processing | 3 Days |
| Optional AI Refinement | 3 Days |
| Quality Validation | 4 Days |
| Storage | 2 Days |
| Orchestration | 3 Days |
| API Layer | 2 Days |
| Admin UI | 3 Days |
| Testing | 5 Days |

Total:

Approximately 7 weeks for final-quality rendering.

MVP without AI refinement:

Approximately 6 weeks.

---

# 11. MVP Technology Stack

Backend:

* FastAPI

Image processing:

* OpenCV
* Pillow
* NumPy
* scikit-image

Background/fabric extraction:

* rembg, only where needed

Storage:

* MinIO or local filesystem

Database:

* PostgreSQL

Testing:

* Pytest
* Golden-image fixtures

Optional AI refinement:

* OpenAI image editing or equivalent provider
* Provider abstraction for future fashion-specific render APIs

Deployment:

* Docker
* Nginx

Server requirement for deterministic rendering:

```text
8 CPU cores
16 GB RAM
100 GB SSD
```

Additional requirement for AI refinement:

```text
External image API key
No local GPU required
```

---

# 12. Final-Quality Acceptance Checklist

A Workflow 2 render is acceptable only if:

* Garment silhouette matches the template.
* Collar, pocket, placket, sleeves, hem, and trims stay in the same locations.
* Buttons remain sharp, aligned, and correctly counted.
* White piping/trim is not contaminated by fabric color.
* Fabric covers all intended fabric regions.
* Fabric texture follows garment parts with believable scale and direction.
* Folds, shadows, seams, and knit/detail remain visible.
* Background is clean and product-photo consistent.
* Output does not look like a flat color overlay.
* Output is suitable as the garment input for Workflow 3 virtual try-on.