Workflow 3 (Updated Architecture)
Customer Virtual Try-On Service (API-Driven Version)

Version: 2.0

1. Objective

The objective of Workflow 3 is to generate a realistic virtual try-on image of a customer wearing a garment that has already been created in Workflow 2.

Unlike the previous architecture that relied on local VTON models such as CatVTON or IDM-VTON, the updated architecture uses external AI image-generation APIs.

This approach significantly reduces infrastructure complexity and eliminates the need for dedicated GPU servers.

Customer Image
+
Rendered Garment Image (Workflow 2)
+
AI Prompt
↓
AI Image Generation API
↓
Final Virtual Try-On Preview
2. High-Level Business Flow
Store Staff Uploads Customer Photo
                ↓

Store Staff Selects Garment Render
(Generated in Workflow 2)
                ↓

System Validates Customer Image
                ↓

System Generates Structured Prompt
                ↓

System Sends Request to AI API
                ↓

AI Generates Try-On Image
                ↓

System Performs Quality Validation
                ↓

Optional Face Restoration/Upscaling
                ↓

Preview Stored
                ↓

Customer Views Final Result
3. Core Philosophy

The system already possesses excellent inputs:

Customer Information
Face Identity
Hair Style
Skin Tone
Body Shape
Body Proportions
Customer Pose
Garment Information
Fabric Texture
Color
Collar Design
Sleeves
Buttons
Pockets
Embroidery
Length
Stitching Pattern

Because Workflow 2 already generates a highly realistic garment image, the external AI model only needs to perform:

Identity Preservation
+
Garment Transfer
+
Photorealistic Composition
4. Updated Technical Pipeline
Upload Customer Image
            ↓

Validate Customer Image
            ↓

Load Rendered Garment
(Workflow 2 Output)
            ↓

Generate AI Prompt
            ↓

Load AI Provider Configuration
(from .env)
            ↓

Call AI Image API
            ↓

Receive Generated Preview
            ↓

Quality Validation
            ↓

Optional Face Restoration
            ↓

Optional Upscaling
            ↓

Store Preview
            ↓

Return Result
5. Workflow Services
Service	Mandatory	Purpose
Customer Validation	Yes	Validate customer image
Garment Retrieval	Yes	Retrieve Workflow 2 output
Prompt Generation	Yes	Create AI instructions
AI Provider Service	Yes	Connect to selected AI API
Image Generation Service	Yes	Generate try-on image
Quality Validation	Recommended	Reject bad outputs
Face Restoration	Optional	Improve face quality
Upscaling	Optional	Generate HD outputs
Storage Service	Yes	Store previews
Audit Logging	Production	Track usage
Consent Management	Production	Privacy compliance
6. Customer Image Validation Service

Purpose:

Reject unsuitable images before API invocation.

Checks:

✓ Single person
✓ Face visible
✓ Full body visible
✓ Front-facing pose preferred
✓ Adequate lighting
✓ Not blurry
✓ Resolution acceptable

Recommended Models:

MVP
Florence-2
Production
Qwen2.5-VL

Output:

{
    "valid": true,
    "reason": ""
}
7. Garment Retrieval Service

Purpose:

Load rendered garment produced in Workflow 2.

Input:

{
    "render_id": "REN_001"
}

Retrieved:

{
    "render_id":"REN_001",
    "rendered_image":"rendered.png",
    "metadata":{
        "category":"shirt",
        "fabric":"cotton",
        "color":"blue"
    }
}
8. Prompt Generation Service

This service dynamically creates prompts for the AI provider.

Example prompt:

Generate a photorealistic fashion photograph.

Use the first image as the customer identity reference.

Preserve exactly:

- facial identity
- hairstyle
- skin tone
- body proportions
- pose

Use the second image as the garment reference.

The customer must wear exactly this garment.

Preserve exactly:

- fabric texture
- color
- collar design
- sleeve design
- buttons
- pockets
- embroidery
- garment length

Do not redesign the garment.

Do not modify the customer's face.

Do not add accessories.

Generate a realistic full-body studio photograph.

Photorealistic.
Fashion photography quality.
Natural cloth draping.
9. AI Provider Service

The platform supports multiple AI providers.

Provider selection is completely configuration-driven.

No code changes are required.

Example:

.env
AI_PROVIDER=openai

OPENAI_API_KEY=xxxxx
OPENAI_MODEL=gpt-image-1
OPENAI_MODEL_VERSION=latest

FASHN_API_KEY=xxxxx

FAL_API_KEY=xxxxx
FAL_MODEL=kolors-virtual-tryon

REPLICATE_API_TOKEN=xxxxx
REPLICATE_MODEL=catvton
REPLICATE_VERSION=xxxxx
10. Provider Selection Architecture
Workflow 3
        ↓

AI Provider Factory
        ↓

Reads .env
        ↓

Loads Provider
        ↓

Invokes Selected API

Example:

provider = settings.AI_PROVIDER

if provider == "openai":
    service = OpenAIProvider()

elif provider == "fashn":
    service = FashnProvider()

elif provider == "fal":
    service = FalProvider()

elif provider == "replicate":
    service = ReplicateProvider()

This architecture enables switching providers without redeploying the system.

11. Supported AI Providers
Provider 1 — OpenAI

Model examples:

gpt-image-1

Strengths:

✓ Excellent instruction following
✓ Strong identity preservation
✓ Multi-image editing
✓ High realism

Recommended for:

MVP
Provider 2 — FASHN AI

Strengths:

✓ Dedicated virtual try-on model
✓ Excellent cloth preservation
✓ Fashion-specific optimization
✓ Production ready

Recommended for:

Production
Provider 3 — Fal AI

Possible hosted models:

Kolors Virtual Try-On
CatVTON
Custom Models

Recommended for:

Advanced deployments
Provider 4 — Replicate

Possible hosted models:

CatVTON
IDM-VTON
Custom Diffusion Models

Recommended for:

Experimentation
12. Image Generation Service

Inputs:

Customer Image
+
Rendered Garment
+
Prompt

Output:

Final Virtual Try-On Image

Example:

{
    "preview_id":"PRE_001",
    "image_url":"preview.png"
}
13. Quality Validation Service

Purpose:

Ensure generated preview satisfies business requirements.

Validation Rules:

✓ Face preserved
✓ Garment preserved
✓ No extra accessories
✓ No body distortion
✓ No missing limbs
✓ No severe artifacts

Possible Models:

CLIP
LPIPS
BRISQUE
14. Optional Enhancement Pipeline
Face Restoration

Recommended:

GFPGAN
CodeFormer
Upscaling

Recommended:

Real-ESRGAN
SwinIR

Pipeline:

Generated Image
        ↓
GFPGAN
        ↓
Real-ESRGAN
        ↓
Final HD Preview
15. Storage Structure
MinIO

previews/

preview_id/

customer.jpg

rendered_garment.png

generated_preview.png

metadata.json

prompt.txt

provider_response.json

processing_log.json
16. Database Schema
previews
id
customer_id
render_id
provider
model
model_version
prompt
storage_path
status
processing_duration
created_by
created_at
metadata
17. API Design
Generate Preview
POST /tryon/render

Request:

multipart/form-data

Fields:

customer_image
render_id

Response:

{
    "job_id":"JOB_001"
}
Get Preview
GET /tryon/render/{id}
List Previews
GET /tryon/previews
Delete Preview
DELETE /tryon/render/{id}
18. Environment Configuration

Example:

# Active provider
AI_PROVIDER=openai

# OpenAI
OPENAI_API_KEY=
OPENAI_MODEL=gpt-image-1
OPENAI_MODEL_VERSION=latest

# FASHN
FASHN_API_KEY=

# Fal
FAL_API_KEY=
FAL_MODEL=kolors-virtual-tryon

# Replicate
REPLICATE_API_TOKEN=
REPLICATE_MODEL=catvton
REPLICATE_MODEL_VERSION=
19. Recommended Deployment Strategy
MVP
Customer Validation
        +
OpenAI GPT Image API

No GPU required.

Production
Customer Validation
        +
FASHN AI API
        +
Quality Validation
Enterprise
Multi-Provider Architecture

Primary:
FASHN AI

Fallback:
OpenAI

Experimental:
Fal AI / Replicate
Final Recommended Architecture
Customer Upload
        ↓
Validation (Florence-2)
        ↓
Load Workflow 2 Garment
        ↓
Prompt Generation
        ↓
Provider Selection (.env)
        ↓
AI Image Generation API
        ↓
Quality Validation
        ↓
GFPGAN (optional)
        ↓
Real-ESRGAN (optional)
        ↓
Storage
        ↓
Customer Preview

This architecture removes almost all GPU infrastructure requirements while maintaining a highly flexible, provider-agnostic virtual try-on workflow.