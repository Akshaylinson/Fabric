from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.adapters import EmbeddingAdapter, MetadataAdapter, SegmentationAdapter

router = APIRouter()

_TEMPLATE_STORE: dict[str, dict[str, Any]] = {}


class TemplateCreateRequest(BaseModel):
    template_name: str | None = None
    front_image_ref: str | None = None
    back_image_ref: str | None = None
    side_image_ref: str | None = None
    image_refs: list[str] = Field(default_factory=list)
    creator_id: str
    creator_name: str


class TemplateReanalyzeRequest(BaseModel):
    reason: str | None = None


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _collect_image_refs(request: TemplateCreateRequest) -> list[str]:
    refs = [
        request.front_image_ref,
        request.back_image_ref,
        request.side_image_ref,
        *request.image_refs,
    ]
    unique_refs: list[str] = []
    for ref in refs:
        if ref and ref not in unique_refs:
            unique_refs.append(ref)
    return unique_refs


def _build_processing_logs(template_id: str, analysis_version: int, action: str) -> list[dict[str, str]]:
    timestamp = _now()
    return [
        {
            "timestamp": timestamp,
            "stage": "ingestion",
            "message": f"{action.title()} received for {template_id}.",
        },
        {
            "timestamp": timestamp,
            "stage": "segmentation",
            "message": f"Segmentation adapter generated masks for analysis version {analysis_version}.",
        },
        {
            "timestamp": timestamp,
            "stage": "metadata",
            "message": "Metadata adapter extracted garment attributes and style notes.",
        },
        {
            "timestamp": timestamp,
            "stage": "embedding",
            "message": "Embedding adapter produced the reusable template vector.",
        },
    ]


def _build_template_package(
    request: TemplateCreateRequest,
    template_id: str,
    analysis_version: int,
    created_at: str,
    updated_at: str,
) -> dict[str, Any]:
    image_refs = _collect_image_refs(request)
    segmentation = SegmentationAdapter().segment(image_refs)
    metadata = MetadataAdapter().extract(image_refs)
    embedding = EmbeddingAdapter().embed(metadata.description)
    template_name = request.template_name or f"Template for {metadata.garment_type.title()}"
    processing_logs = _build_processing_logs(
        template_id=template_id,
        analysis_version=analysis_version,
        action="template analysis",
    )

    package = {
        "template_id": template_id,
        "template_name": template_name,
        "preview_image": f"minio://templates/{template_id}/preview.png",
        "source_image_refs": image_refs,
        "segmentation_masks": segmentation.masks,
        "metadata": {
            **metadata.__dict__,
            "source_image_count": len(image_refs),
        },
        "description": metadata.description,
        "embedding_vector": embedding.vector,
        "created_at": created_at,
        "updated_at": updated_at,
        "analysis_version": analysis_version,
        "creator": {
            "id": request.creator_id,
            "name": request.creator_name,
        },
        "processing_logs": processing_logs,
    }
    package["template_package"] = {
        "template_id": package["template_id"],
        "template_name": package["template_name"],
        "preview_image": package["preview_image"],
        "segmentation_masks": package["segmentation_masks"],
        "metadata": package["metadata"],
        "description": package["description"],
        "embedding_vector": package["embedding_vector"],
        "created_at": package["created_at"],
        "updated_at": package["updated_at"],
        "analysis_version": package["analysis_version"],
        "creator": package["creator"],
        "source_image_refs": package["source_image_refs"],
    }
    package["analysis_history"] = [
        {
            "version": analysis_version,
            "timestamp": updated_at,
            "event": "created" if analysis_version == 1 else "reanalyzed",
            "processing_logs": processing_logs,
        }
    ]
    return package


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "template-service"}


@router.get("/templates")
def list_templates() -> dict[str, list[dict[str, Any]]]:
    return {
        "items": [
            {
                "template_id": template["template_id"],
                "template_name": template["template_name"],
                "created_at": template["created_at"],
                "updated_at": template["updated_at"],
                "analysis_version": template["analysis_version"],
            }
            for template in _TEMPLATE_STORE.values()
        ]
    }


@router.post("/templates/from-images")
def create_template(request: TemplateCreateRequest) -> dict[str, Any]:
    template_id = f"tpl_{uuid4().hex[:12]}"
    created_at = _now()
    package = _build_template_package(
        request=request,
        template_id=template_id,
        analysis_version=1,
        created_at=created_at,
        updated_at=created_at,
    )
    _TEMPLATE_STORE[template_id] = package
    return package


@router.get("/templates/{template_id}")
def get_template(template_id: str) -> dict[str, Any]:
    template = _TEMPLATE_STORE.get(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.post("/templates/{template_id}/reanalyze")
def reanalyze_template(template_id: str, request: TemplateReanalyzeRequest) -> dict[str, Any]:
    template = _TEMPLATE_STORE.get(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    creator = template["creator"]
    source_image_refs = template["source_image_refs"]
    create_request = TemplateCreateRequest(
        template_name=template["template_name"],
        front_image_ref=source_image_refs[0] if len(source_image_refs) > 0 else None,
        back_image_ref=source_image_refs[1] if len(source_image_refs) > 1 else None,
        side_image_ref=source_image_refs[2] if len(source_image_refs) > 2 else None,
        image_refs=source_image_refs,
        creator_id=creator["id"],
        creator_name=creator["name"],
    )
    next_version = int(template["analysis_version"]) + 1
    updated_at = _now()
    refreshed = _build_template_package(
        request=create_request,
        template_id=template_id,
        analysis_version=next_version,
        created_at=template["created_at"],
        updated_at=updated_at,
    )
    refreshed["analysis_history"] = [
        *template.get("analysis_history", []),
        {
            "version": next_version,
            "timestamp": updated_at,
            "event": "reanalyzed",
            "reason": request.reason or "Manual QA rerun",
            "processing_logs": refreshed["processing_logs"],
        },
    ]
    _TEMPLATE_STORE[template_id] = refreshed
    return refreshed
