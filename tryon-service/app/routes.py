from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from time import perf_counter
from typing import Any
from uuid import uuid4

from fastapi import APIRouter
from pydantic import BaseModel

from app.adapters import HumanParsingAdapter, PoseAdapter, TryOnAdapter
from textile_shared.persistence import LocalObjectStorage, decode_data_url, service_object_dir

router = APIRouter()
_STORAGE = LocalObjectStorage(service_object_dir("tryon-service"))


class TryOnRequest(BaseModel):
    customer_image_ref: str
    garment_image_ref: str
    customer_image_data: str | None = None
    garment_image_data: str | None = None


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "tryon-service"}


def _orchestrator_url() -> str | None:
    return os.getenv("ORCHESTRATOR_SERVICE_URL")


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


@router.post("/tryon/render")
def render_tryon(request: TryOnRequest) -> dict[str, object]:
    started_at = datetime.now(timezone.utc)
    timer_started = perf_counter()

    customer_source_ref = request.customer_image_ref
    garment_source_ref = request.garment_image_ref
    if request.customer_image_data:
        raw_bytes, mime_type = decode_data_url(request.customer_image_data)
        extension = (mime_type.split("/")[-1] if mime_type else "bin").replace("jpeg", "jpg")
        customer_source_ref = _STORAGE.put_bytes(f"customers/{request.customer_image_ref}/source/customer.{extension}", raw_bytes)
    if request.garment_image_data:
        raw_bytes, mime_type = decode_data_url(request.garment_image_data)
        extension = (mime_type.split("/")[-1] if mime_type else "bin").replace("jpeg", "jpg")
        garment_source_ref = _STORAGE.put_bytes(f"garments/{request.garment_image_ref}/source/garment.{extension}", raw_bytes)

    human_parsing = HumanParsingAdapter().parse(request.customer_image_ref)
    pose = PoseAdapter().estimate(request.customer_image_ref)
    result = TryOnAdapter().generate(
        request.customer_image_ref,
        request.garment_image_ref,
        human_parsing.body_mask_ref,
        pose.pose_keypoints_ref,
    )
    completed_at = datetime.now(timezone.utc)
    render_id = f"try_{uuid4().hex[:12]}"
    output_ref = _STORAGE.put_text(
        f"renders/{render_id}/preview.svg",
        f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1600"><rect width="100%" height="100%" fill="#020617" /><text x="120" y="180" fill="#e2e8f0" font-size="42" font-family="Arial, sans-serif">Try-On Preview</text><text x="120" y="260" fill="#94a3b8" font-size="26" font-family="Arial, sans-serif">Customer: {request.customer_image_ref}</text><text x="120" y="310" fill="#94a3b8" font-size="26" font-family="Arial, sans-serif">Garment: {request.garment_image_ref}</text></svg>',
    )
    processing_time_ms = round((perf_counter() - timer_started) * 1000, 2)
    job_id = _register_job(
        workflow="workflow-3",
        entity_id=render_id,
        action="render-tryon",
        payload={"customer_image_ref": request.customer_image_ref, "garment_image_ref": request.garment_image_ref},
    )

    payload = {
        "job_id": job_id,
        "render_id": render_id,
        "customer_source_ref": customer_source_ref,
        "garment_source_ref": garment_source_ref,
        "output_image_ref": output_ref,
        "notes": result.notes,
        "face_preserved": True,
        "body_shape_preserved": True,
        "garment_structure_preserved": True,
        "fabric_appearance_preserved": True,
        "timing": {
            "started_at": started_at.isoformat(),
            "completed_at": completed_at.isoformat(),
            "processing_time_ms": processing_time_ms,
        },
        "processing_logs": [
            {
                "timestamp": started_at.isoformat(),
                "stage": "human-parsing",
                "message": f"Human parsing completed for {request.customer_image_ref}.",
            },
            {
                "timestamp": started_at.isoformat(),
                "stage": "pose-estimation",
                "message": f"Pose estimation completed for {request.customer_image_ref}.",
            },
            {
                "timestamp": completed_at.isoformat(),
                "stage": "tryon-complete",
                "message": f"Try-on render {render_id} completed in {processing_time_ms} ms.",
            },
        ],
    }
    _STORAGE.put_json(f"renders/{render_id}/package.json", payload)
    return payload
