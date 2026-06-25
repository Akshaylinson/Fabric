from datetime import datetime, timezone
from time import perf_counter
from uuid import uuid4

from fastapi import APIRouter
from pydantic import BaseModel

from app.adapters import FabricTransferAdapter, TextureMappingAdapter

router = APIRouter()


class FabricRenderRequest(BaseModel):
    fabric_ref: str
    template_ref: str
    comparison_render_ref: str | None = None
    render_label: str | None = None


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "fabric-service"}


@router.post("/fabric/render")
def render_fabric(request: FabricRenderRequest) -> dict[str, object]:
    started_at = datetime.now(timezone.utc)
    timer_started = perf_counter()

    transfer = FabricTransferAdapter().transfer(request.fabric_ref, request.template_ref)
    mapping = TextureMappingAdapter().map_texture(request.fabric_ref, request.template_ref)

    completed_at = datetime.now(timezone.utc)
    processing_time_ms = round((perf_counter() - timer_started) * 1000, 2)
    render_id = f"rnd_{uuid4().hex[:12]}"
    version_label = "v2" if request.comparison_render_ref else "v1"
    comparison = (
        {
            "base_render_ref": request.comparison_render_ref,
            "current_version": version_label,
            "compared_version": "v1",
            "summary": "Mock comparison confirms the fabric update preserved garment structure while changing appearance.",
        }
        if request.comparison_render_ref
        else None
    )

    return {
        "render_id": render_id,
        "render_label": request.render_label or f"Fabric Render for {request.template_ref.split('/')[-1]}",
        "status": "completed",
        "template_ref": request.template_ref,
        "fabric_ref": request.fabric_ref,
        "rendered_image_ref": transfer.rendered_image_ref,
        "version_label": version_label,
        "metadata": {
            "preserved_structure": mapping.preserved_structure,
            "fabric_fit": "applied",
            "texture_strategy": "mock_tiled_texture",
            "garment_area_covered": "98.6%",
        },
        "comparison": comparison,
        "version_history": [
            {
                "version": "v1",
                "render_ref": request.comparison_render_ref or render_id,
                "label": request.comparison_render_ref or "Current render baseline",
            },
            {
                "version": version_label,
                "render_ref": render_id,
                "label": request.render_label or "Current render",
            },
        ],
        "timing": {
            "started_at": started_at.isoformat(),
            "completed_at": completed_at.isoformat(),
            "processing_time_ms": processing_time_ms,
        },
        "processing_logs": [
            {
                "timestamp": started_at.isoformat(),
                "stage": "render-request",
                "message": f"Received render request for {request.template_ref} using {request.fabric_ref}.",
            },
            {
                "timestamp": started_at.isoformat(),
                "stage": "texture-mapping",
                "message": "Texture mapping adapter preserved garment structure and applied fabric appearance.",
            },
            {
                "timestamp": completed_at.isoformat(),
                "stage": "render-complete",
                "message": f"Render {render_id} completed in {processing_time_ms} ms.",
            },
        ],
        "notes": mapping.notes,
    }
