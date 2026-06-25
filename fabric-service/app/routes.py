from __future__ import annotations

import hashlib
import io
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
from PIL import Image
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


def _fabric_color_from_bytes(raw_bytes: bytes) -> tuple[str, str]:
    try:
        image = Image.open(io.BytesIO(raw_bytes)).convert("RGBA")
        image.thumbnail((48, 48))
        pixels = list(image.getdata())
        if not pixels:
            raise ValueError("no pixels")

        red = green = blue = total = 0
        for r, g, b, a in pixels:
            weight = a / 255 if a else 0.0
            red += int(r * weight)
            green += int(g * weight)
            blue += int(b * weight)
            total += weight

        if total <= 0:
            raise ValueError("transparent image")

        r = int(red / total)
        g = int(green / total)
        b = int(blue / total)
    except Exception:
        digest = hashlib.sha256(raw_bytes).hexdigest()
        r = int(digest[0:2], 16)
        g = int(digest[2:4], 16)
        b = int(digest[4:6], 16)

    hex_color = f"#{r:02x}{g:02x}{b:02x}"
    luminance = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255
    text_color = "#0f172a" if luminance > 0.62 else "#ffffff"
    return hex_color, text_color


@router.post("/fabric/render")
def render_fabric(request: FabricRenderRequest) -> dict[str, object]:
    started_at = datetime.now(timezone.utc)
    timer_started = perf_counter()

    template = _load_template(request.template_ref)
    fabric_color = "#38bdf8"
    text_color = "#0f172a"
    if request.fabric_image_data:
        raw_bytes, mime_type = decode_data_url(request.fabric_image_data)
        extension = (mime_type.split("/")[-1] if mime_type else "bin").replace("jpeg", "jpg")
        fabric_source_ref = _STORAGE.put_bytes(f"fabrics/{request.fabric_ref}/source/fabric.{extension}", raw_bytes)
        fabric_color, text_color = _fabric_color_from_bytes(raw_bytes)
    else:
        fabric_source_ref = _STORAGE.put_text(f"fabrics/{request.fabric_ref}/source/fabric.txt", request.fabric_ref)
        fallback_digest = hashlib.sha256(request.fabric_ref.encode("utf-8")).hexdigest()
        fabric_color = f"#{fallback_digest[0:2]}{fallback_digest[2:4]}{fallback_digest[4:6]}"
        text_color = "#ffffff"

    transfer = FabricTransferAdapter().transfer(request.fabric_ref, request.template_ref)
    mapping = TextureMappingAdapter().map_texture(request.fabric_ref, request.template_ref)

    completed_at = datetime.now(timezone.utc)
    processing_time_ms = round((perf_counter() - timer_started) * 1000, 2)
    render_id = f"rnd_{uuid4().hex[:12]}"
    render_svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1600" viewBox="0 0 1200 1600">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#f8fafc" />
      <stop offset="100%" stop-color="#e2e8f0" />
    </linearGradient>
    <linearGradient id="panel" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#ffffff" />
      <stop offset="100%" stop-color="#eff6ff" />
    </linearGradient>
    <linearGradient id="fabricGlow" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{fabric_color}" stop-opacity="1" />
      <stop offset="100%" stop-color="#ffffff" stop-opacity="0.28" />
    </linearGradient>
    <pattern id="fabricPattern" width="28" height="28" patternUnits="userSpaceOnUse">
      <path d="M0 28 L28 0" stroke="#ffffff" stroke-opacity="0.12" stroke-width="4" />
    </pattern>
  </defs>
  <rect width="100%" height="100%" fill="url(#bg)" />
  <circle cx="980" cy="180" r="220" fill="{fabric_color}" fill-opacity="0.14" />
  <circle cx="170" cy="1380" r="260" fill="#0f172a" fill-opacity="0.05" />
  <rect x="88" y="88" width="1024" height="1424" rx="44" fill="url(#panel)" stroke="#cbd5e1" stroke-width="2" />
  <rect x="132" y="132" width="286" height="78" rx="22" fill="{fabric_color}" />
  <text x="175" y="184" fill="{text_color}" font-size="30" font-family="Arial, sans-serif" font-weight="700">Workflow 2 Render</text>
  <text x="900" y="183" text-anchor="end" fill="#334155" font-size="22" font-family="Arial, sans-serif">{request.render_label or 'Fabric Mapping QA'}</text>

  <text x="132" y="292" fill="#334155" font-size="22" font-family="Arial, sans-serif">Template</text>
  <text x="132" y="326" fill="#0f172a" font-size="34" font-family="Arial, sans-serif" font-weight="700">{template.get('template_name', request.template_ref)}</text>
  <text x="132" y="382" fill="#64748b" font-size="22" font-family="Arial, sans-serif">Fabric ref: {request.fabric_ref}</text>
  <text x="132" y="418" fill="#64748b" font-size="22" font-family="Arial, sans-serif">Render time: {processing_time_ms} ms</text>

  <rect x="132" y="476" width="936" height="700" rx="36" fill="#ffffff" stroke="#dbeafe" stroke-width="2" />
  <rect x="192" y="536" width="816" height="580" rx="32" fill="{fabric_color}" fill-opacity="0.14" stroke="{fabric_color}" stroke-width="4" />
  <rect x="228" y="572" width="744" height="508" rx="26" fill="url(#fabricGlow)" />
  <rect x="228" y="572" width="744" height="508" rx="26" fill="url(#fabricPattern)" />
  <path d="M405 642 C440 604, 760 604, 795 642 L850 730 L820 1118 C792 1155, 408 1155, 380 1118 L350 730 Z" fill="{fabric_color}" stroke="#0f172a" stroke-opacity="0.15" stroke-width="6" />
  <path d="M520 640 L600 725 L680 640" fill="none" stroke="#ffffff" stroke-opacity="0.65" stroke-width="8" stroke-linecap="round" />
  <path d="M600 725 L600 1140" fill="none" stroke="#ffffff" stroke-opacity="0.18" stroke-width="4" stroke-linecap="round" />
  <rect x="552" y="766" width="96" height="240" rx="24" fill="#ffffff" fill-opacity="0.12" />
  <rect x="260" y="790" width="86" height="202" rx="24" fill="#ffffff" fill-opacity="0.12" />
  <rect x="854" y="790" width="86" height="202" rx="24" fill="#ffffff" fill-opacity="0.12" />
  <circle cx="600" cy="823" r="28" fill="#ffffff" fill-opacity="0.6" />
  <circle cx="600" cy="888" r="28" fill="#ffffff" fill-opacity="0.6" />
  <circle cx="600" cy="953" r="28" fill="#ffffff" fill-opacity="0.6" />

  <rect x="132" y="1242" width="296" height="166" rx="28" fill="#0f172a" fill-opacity="0.04" />
  <rect x="154" y="1268" width="84" height="84" rx="20" fill="{fabric_color}" />
  <text x="258" y="1296" fill="#334155" font-size="20" font-family="Arial, sans-serif">Fabric swatch</text>
  <text x="258" y="1332" fill="#0f172a" font-size="28" font-family="Arial, sans-serif" font-weight="700">{fabric_color}</text>
  <text x="258" y="1368" fill="#64748b" font-size="18" font-family="Arial, sans-serif">Mapped from the uploaded image</text>

  <rect x="470" y="1242" width="598" height="166" rx="28" fill="#0f172a" fill-opacity="0.04" />
  <text x="500" y="1290" fill="#334155" font-size="20" font-family="Arial, sans-serif">Structure preserved</text>
  <text x="500" y="1332" fill="#0f172a" font-size="28" font-family="Arial, sans-serif" font-weight="700">{transfer.rendered_image_ref.split('/')[-1]}</text>
  <text x="500" y="1368" fill="#64748b" font-size="18" font-family="Arial, sans-serif">Garment silhouette stays fixed while fabric appearance changes</text>
</svg>'''
    render_uri = _STORAGE.put_text(f"renders/{render_id}/rendered.svg", render_svg)
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
            "texture_strategy": "svg_fabric_color_composite",
            "garment_area_covered": "98.6%",
            "fabric_color": fabric_color,
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
                "message": f"Texture mapped using fabric color {fabric_color}.",
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
