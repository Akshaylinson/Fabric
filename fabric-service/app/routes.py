from fastapi import APIRouter
from pydantic import BaseModel

from app.adapters import FabricTransferAdapter, TextureMappingAdapter

router = APIRouter()


class FabricRenderRequest(BaseModel):
    fabric_ref: str
    template_ref: str


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "fabric-service"}


@router.post("/fabric/render")
def render_fabric(request: FabricRenderRequest) -> dict[str, object]:
    transfer = FabricTransferAdapter().transfer(request.fabric_ref, request.template_ref)
    mapping = TextureMappingAdapter().map_texture(request.fabric_ref, request.template_ref)
    return {
        "rendered_image_ref": transfer.rendered_image_ref,
        "preserved_structure": mapping.preserved_structure,
        "notes": mapping.notes,
    }

