from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.adapters import EmbeddingAdapter, MetadataAdapter, SegmentationAdapter

router = APIRouter()


class TemplateCreateRequest(BaseModel):
    image_refs: list[str] = Field(default_factory=list)
    creator_id: str
    creator_name: str


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "template-service"}


@router.post("/templates/from-images")
def create_template(request: TemplateCreateRequest) -> dict[str, object]:
    segmentation = SegmentationAdapter().segment(request.image_refs)
    metadata = MetadataAdapter().extract(request.image_refs)
    embedding = EmbeddingAdapter().embed(metadata.description)
    template_id = f"tpl_{uuid4().hex[:12]}"

    return {
        "template_id": template_id,
        "template_name": f"Template for {metadata.garment_type}",
        "preview_image": f"minio://templates/{template_id}/preview.png",
        "segmentation_masks": segmentation.masks,
        "metadata": metadata.__dict__,
        "description": metadata.description,
        "embedding_vector": embedding.vector,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "creator": {
            "id": request.creator_id,
            "name": request.creator_name,
        },
    }

