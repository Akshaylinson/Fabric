from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.adapters import EmbeddingAdapter, MetadataAdapter, SegmentationAdapter
from textile_shared.persistence import (
    LocalObjectStorage,
    PersistentJsonStore,
    decode_data_url,
    service_object_dir,
    service_state_dir,
)

router = APIRouter()

_STORAGE = LocalObjectStorage(service_object_dir("template-service"))
_TEMPLATES = PersistentJsonStore(service_state_dir("template-service") / "templates.json", default_factory=dict)


class TemplateCreateRequest(BaseModel):
    template_name: str | None = None
    front_image_ref: str | None = None
    back_image_ref: str | None = None
    side_image_ref: str | None = None
    front_image_data: str | None = None
    back_image_data: str | None = None
    side_image_data: str | None = None
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


def _service_url() -> str | None:
    return os.getenv("ORCHESTRATOR_SERVICE_URL")


def _register_job(workflow: str, entity_id: str, action: str, payload: dict[str, Any]) -> str | None:
    base_url = _service_url()
    if not base_url:
        return None

    request_body = json.dumps(
        {
            "workflow": workflow,
            "entity_id": entity_id,
            "action": action,
            "status": "completed",
            "payload": payload,
        }
    ).encode("utf-8")

    request = urllib.request.Request(
        f"{base_url}/jobs",
        data=request_body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            body = json.loads(response.read().decode("utf-8"))
            return body.get("job_id")
    except (urllib.error.URLError, TimeoutError, ValueError):
        return None


def _store_image(template_id: str, label: str, ref: str | None, data_url: str | None) -> dict[str, str]:
    if data_url:
        raw_bytes, mime_type = decode_data_url(data_url)
        extension = (mime_type.split("/")[-1] if mime_type else "bin").replace("jpeg", "jpg")
        key = f"templates/{template_id}/source/{label}.{extension}"
        uri = _STORAGE.put_bytes(key, raw_bytes)
        return {"ref": ref or label, "storage_uri": uri}

    placeholder_key = f"templates/{template_id}/source/{label}.txt"
    uri = _STORAGE.put_text(placeholder_key, ref or f"{label}_missing")
    return {"ref": ref or label, "storage_uri": uri}


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
    existing_history: list[dict[str, Any]] | None = None,
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

    stored_images = {
        "front": _store_image(template_id, "front", request.front_image_ref, request.front_image_data),
        "back": _store_image(template_id, "back", request.back_image_ref, request.back_image_data),
        "side": _store_image(template_id, "side", request.side_image_ref, request.side_image_data),
    }

    preview_source = request.front_image_data or request.back_image_data or request.side_image_data
    if preview_source:
        preview_bytes, _mime = decode_data_url(preview_source)
        preview_uri = _STORAGE.put_bytes(f"templates/{template_id}/preview/preview.png", preview_bytes)
    else:
        preview_uri = _STORAGE.put_text(f"templates/{template_id}/preview/preview.png", f"preview for {template_id}")

    mask_uris = [
        _STORAGE.put_json(f"templates/{template_id}/masks/{mask_name}.json", {"template_id": template_id, "mask_name": mask_name, "source_ref": ref})
        for mask_name, ref in zip(["front", "back", "side"], image_refs[:3], strict=False)
    ]

    package = {
        "template_id": template_id,
        "template_name": template_name,
        "preview_image": preview_uri,
        "source_image_refs": image_refs,
        "source_images": stored_images,
        "segmentation_masks": mask_uris or segmentation.masks,
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
        "storage": {
            "preview_image": preview_uri,
            "mask_files": mask_uris,
        },
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
        "storage": package["storage"],
    }
    package["analysis_history"] = [
        *(existing_history or []),
        {
            "version": analysis_version,
            "timestamp": updated_at,
            "event": "created" if analysis_version == 1 else "reanalyzed",
            "processing_logs": processing_logs,
        },
    ]
    return package


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "template-service"}


@router.get("/templates")
def list_templates() -> dict[str, list[dict[str, Any]]]:
    templates = _TEMPLATES.load()
    return {
        "items": [
            {
                "template_id": template["template_id"],
                "template_name": template["template_name"],
                "created_at": template["created_at"],
                "updated_at": template["updated_at"],
                "analysis_version": template["analysis_version"],
            }
            for template in templates.values()
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
    templates = _TEMPLATES.load()
    templates[template_id] = package
    _TEMPLATES.save(templates)
    package["job_id"] = _register_job(
        workflow="workflow-1",
        entity_id=template_id,
        action="create-template",
        payload={"template_id": template_id, "template_name": package["template_name"]},
    )
    templates[template_id] = package
    _TEMPLATES.save(templates)
    _STORAGE.put_json(f"templates/{template_id}/package.json", package)
    return package


@router.get("/templates/{template_id}")
def get_template(template_id: str) -> dict[str, Any]:
    templates = _TEMPLATES.load()
    template = templates.get(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.post("/templates/{template_id}/reanalyze")
def reanalyze_template(template_id: str, request: TemplateReanalyzeRequest) -> dict[str, Any]:
    templates = _TEMPLATES.load()
    template = templates.get(template_id)
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
        existing_history=template.get("analysis_history", []),
    )
    refreshed["analysis_history"][-1]["reason"] = request.reason or "Manual QA rerun"
    refreshed["job_id"] = _register_job(
        workflow="workflow-1",
        entity_id=template_id,
        action="reanalyze-template",
        payload={"template_id": template_id, "reason": request.reason or "Manual QA rerun"},
    )
    templates[template_id] = refreshed
    _TEMPLATES.save(templates)
    _STORAGE.put_json(f"templates/{template_id}/package.json", refreshed)
    return refreshed
