from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.adapters import FabricTransferAdapter, TextureMappingAdapter
from textile_shared.persistence import (
    LocalObjectStorage,
    decode_data_url,
    service_object_dir,
    service_state_dir,
)

router = APIRouter()

_STORAGE = LocalObjectStorage(service_object_dir("fabric-service"))
_RENDER_STATE = service_state_dir("fabric-service") / "renders.json"


class FabricRenderRequest(BaseModel):
    fabric_ref: str
    template_ref: str
    fabric_image_data: str | None = None
    comparison_render_ref: str | None = None
    render_label: str | None = None


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "fabric-service"}


def _template_service_url() -> str:
    return os.getenv("TEMPLATE_SERVICE_URL", "http://template-service:8001")


def _orchestrator_url() -> str | None:
    return os.getenv("ORCHESTRATOR_SERVICE_URL")


def _load_template(template_ref: str) -> dict[str, Any]:
    request = urllib.request.Request(f"{_template_service_url()}/templates/{template_ref}")
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            raise HTTPException(status_code=404, detail="Template not found") from exc
        raise HTTPException(status_code=502, detail="Unable to load template") from exc
    except urllib.error.URLError as exc:
        raise HTTPException(status_code=502, detail="Template service unavailable") from exc


def _register_job(workflow: str, entity_id: str, action: str, payload: dict[str, Any]) -> str | None:
    base_url = _orchestrator_url()
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


def _render_image_path(render_id: str) -> Path:
    svg_path = _STORAGE.path_for(f"renders/{render_id}/rendered.svg")
    if svg_path.exists():
        return svg_path

    return _STORAGE.path_for(f"renders/{render_id}/rendered.png")


@router.get("/renders/{render_id}/image")
def get_render_image(render_id: str):
    image_path = _render_image_path(render_id)
    if not image_path.exists():
        raise HTTPException(status_code=404, detail="Render image not found")

    media_type = "image/svg+xml" if image_path.suffix.lower() == ".svg" else "image/png"
    return FileResponse(image_path, media_type=media_type, headers={"Cache-Control": "no-store"})


@router.post("/fabric/render")
def render_fabric(request: FabricRenderRequest) -> dict[str, object]:
    started_at = datetime.now(timezone.utc)
    timer_started = perf_counter()

    template = _load_template(request.template_ref)
    if request.fabric_image_data:
        raw_bytes, mime_type = decode_data_url(request.fabric_image_data)
        extension = (mime_type.split("/")[-1] if mime_type else "bin").replace("jpeg", "jpg")
        fabric_source_ref = _STORAGE.put_bytes(f"fabrics/{request.fabric_ref}/source/fabric.{extension}", raw_bytes)
    else:
        fabric_source_ref = _STORAGE.put_text(f"fabrics/{request.fabric_ref}/source/fabric.txt", request.fabric_ref)

    transfer = FabricTransferAdapter().transfer(request.fabric_ref, request.template_ref)
    mapping = TextureMappingAdapter().map_texture(request.fabric_ref, request.template_ref)

    completed_at = datetime.now(timezone.utc)
    processing_time_ms = round((perf_counter() - timer_started) * 1000, 2)
    render_id = f"rnd_{uuid4().hex[:12]}"
    render_uri = _STORAGE.put_text(
        f"renders/{render_id}/rendered.svg",
        f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1600" viewBox="0 0 1200 1600">
  <rect width="100%" height="100%" fill="#0f172a" />
  <rect x="120" y="180" width="960" height="1240" rx="48" fill="#111827" stroke="#22d3ee" stroke-opacity="0.35" />
  <text x="160" y="280" fill="#e2e8f0" font-size="44" font-family="Arial, sans-serif">{request.render_label or 'Workflow 2 Render'}</text>
  <text x="160" y="360" fill="#94a3b8" font-size="26" font-family="Arial, sans-serif">Template: {request.template_ref}</text>
  <text x="160" y="410" fill="#94a3b8" font-size="26" font-family="Arial, sans-serif">Fabric: {request.fabric_ref}</text>
  <rect x="180" y="520" width="840" height="720" rx="36" fill="#1e293b" stroke="#38bdf8" stroke-opacity="0.2" />
  <text x="600" y="880" text-anchor="middle" fill="#cbd5e1" font-size="36" font-family="Arial, sans-serif">Mock garment render</text>
  <text x="600" y="930" text-anchor="middle" fill="#94a3b8" font-size="24" font-family="Arial, sans-serif">Structure preserved, fabric appearance mapped</text>
  <text x="600" y="1060" text-anchor="middle" fill="#67e8f9" font-size="22" font-family="Arial, sans-serif">{fabric_source_ref}</text>
</svg>''',
    )
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

    job_id = _register_job(
        workflow="workflow-2",
        entity_id=render_id,
        action="render-fabric",
        payload={
            "template_ref": request.template_ref,
            "fabric_ref": request.fabric_ref,
            "render_id": render_id,
        },
    )

    payload: dict[str, Any] = {
        "render_id": render_id,
        "job_id": job_id,
        "render_label": request.render_label or f"Fabric Render for {request.template_ref.split('/')[-1]}",
        "status": "completed",
        "template_ref": request.template_ref,
        "template_snapshot": template,
        "fabric_ref": request.fabric_ref,
        "fabric_source_ref": fabric_source_ref,
        "rendered_image_ref": render_uri,
        "version_label": version_label,
        "metadata": {
            "preserved_structure": mapping.preserved_structure,
            "fabric_fit": "applied",
            "texture_strategy": "svg_mock_composite",
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
                "stage": "template-load",
                "message": f"Template {request.template_ref} loaded from the template service.",
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
    _STORAGE.put_json(f"renders/{render_id}/metadata.json", payload["metadata"])
    _STORAGE.put_json(f"renders/{render_id}/logs.json", payload["processing_logs"])
    _STORAGE.put_json(f"renders/{render_id}/package.json", payload)
    return payload
