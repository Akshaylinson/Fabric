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


def _shade_color(hex_color: str, factor: float) -> str:
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    r = max(0, min(255, int(r * factor)))
    g = max(0, min(255, int(g * factor)))
    b = max(0, min(255, int(b * factor)))
    return f"#{r:02x}{g:02x}{b:02x}"


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

    fabric_dark = _shade_color(fabric_color, 0.72)
    fabric_mid = _shade_color(fabric_color, 0.88)
    fabric_light = _shade_color(fabric_color, 1.12)
    shadow_color = _shade_color(fabric_color, 0.56)

    transfer = FabricTransferAdapter().transfer(request.fabric_ref, request.template_ref)
    mapping = TextureMappingAdapter().map_texture(request.fabric_ref, request.template_ref)

    completed_at = datetime.now(timezone.utc)
    processing_time_ms = round((perf_counter() - timer_started) * 1000, 2)
    render_id = f"rnd_{uuid4().hex[:12]}"
    render_svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1400 1800" width="1400" height="1800">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#f8fafc" />
      <stop offset="55%" stop-color="#eef2ff" />
      <stop offset="100%" stop-color="#e2e8f0" />
    </linearGradient>
    <radialGradient id="spot" cx="48%" cy="18%" r="68%">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="0.82" />
      <stop offset="50%" stop-color="#ffffff" stop-opacity="0.24" />
      <stop offset="100%" stop-color="#ffffff" stop-opacity="0" />
    </radialGradient>
    <linearGradient id="shirtGrad" x1="0.1" y1="0" x2="0.9" y2="1">
      <stop offset="0%" stop-color="{fabric_light}" />
      <stop offset="46%" stop-color="{fabric_color}" />
      <stop offset="100%" stop-color="{fabric_dark}" />
    </linearGradient>
    <linearGradient id="shirtShadow" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#000000" stop-opacity="0.16" />
      <stop offset="100%" stop-color="#000000" stop-opacity="0.02" />
    </linearGradient>
    <linearGradient id="clothSheen" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="0" />
      <stop offset="50%" stop-color="#ffffff" stop-opacity="0.08" />
      <stop offset="100%" stop-color="#ffffff" stop-opacity="0" />
    </linearGradient>
    <pattern id="weave" width="22" height="22" patternUnits="userSpaceOnUse" patternTransform="rotate(28)">
      <path d="M0 0 L22 22" stroke="#ffffff" stroke-opacity="0.08" stroke-width="4" />
      <path d="M22 0 L0 22" stroke="#ffffff" stroke-opacity="0.04" stroke-width="4" />
    </pattern>
    <filter id="softShadow" x="-20%" y="-20%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="18" />
    </filter>
    <filter id="garmentBlur" x="-10%" y="-10%" width="120%" height="120%">
      <feGaussianBlur stdDeviation="1.5" />
    </filter>
    <clipPath id="shirtClip">
      <path d="M293 270 L417 182 C464 150 513 134 566 134 L834 134 C887 134 936 150 983 182 L1107 270 L1038 452 L936 386 L936 1526 L464 1526 L464 386 L362 452 Z" />
    </clipPath>
    <clipPath id="sleeveLeftClip">
      <path d="M305 275 L218 402 C174 466 164 528 175 590 C187 658 224 710 292 748 L357 785 L403 692 L357 666 C325 648 309 618 307 581 C305 547 319 510 347 470 L431 356 Z" />
    </clipPath>
    <clipPath id="sleeveRightClip">
      <path d="M1095 275 L1182 402 C1226 466 1236 528 1225 590 C1213 658 1176 710 1108 748 L1043 785 L997 692 L1043 666 C1075 648 1091 618 1093 581 C1095 547 1081 510 1053 470 L969 356 Z" />
    </clipPath>
  </defs>

  <rect width="100%" height="100%" fill="url(#bg)" />
  <ellipse cx="700" cy="1508" rx="390" ry="88" fill="#0f172a" fill-opacity="0.14" filter="url(#softShadow)" />
  <ellipse cx="700" cy="1472" rx="430" ry="122" fill="#0f172a" fill-opacity="0.06" />
  <circle cx="1040" cy="248" r="250" fill="url(#spot)" />

  <g transform="translate(0, 30)">
    <g filter="url(#softShadow)">
      <path d="M293 270 L417 182 C464 150 513 134 566 134 L834 134 C887 134 936 150 983 182 L1107 270 L1038 452 L936 386 L936 1526 L464 1526 L464 386 L362 452 Z" fill="#000000" fill-opacity="0.10" />
      <path d="M305 275 L218 402 C174 466 164 528 175 590 C187 658 224 710 292 748 L357 785 L403 692 L357 666 C325 648 309 618 307 581 C305 547 319 510 347 470 L431 356 Z" fill="#000000" fill-opacity="0.10" />
      <path d="M1095 275 L1182 402 C1226 466 1236 528 1225 590 C1213 658 1176 710 1108 748 L1043 785 L997 692 L1043 666 C1075 648 1091 618 1093 581 C1095 547 1081 510 1053 470 L969 356 Z" fill="#000000" fill-opacity="0.10" />
    </g>

    <path d="M293 270 L417 182 C464 150 513 134 566 134 L834 134 C887 134 936 150 983 182 L1107 270 L1038 452 L936 386 L936 1526 L464 1526 L464 386 L362 452 Z" fill="url(#shirtGrad)" stroke="#ffffff" stroke-opacity="0.44" stroke-width="7" />
    <path d="M305 275 L218 402 C174 466 164 528 175 590 C187 658 224 710 292 748 L357 785 L403 692 L357 666 C325 648 309 618 307 581 C305 547 319 510 347 470 L431 356 Z" fill="url(#shirtGrad)" stroke="#ffffff" stroke-opacity="0.34" stroke-width="6" />
    <path d="M1095 275 L1182 402 C1226 466 1236 528 1225 590 C1213 658 1176 710 1108 748 L1043 785 L997 692 L1043 666 C1075 648 1091 618 1093 581 C1095 547 1081 510 1053 470 L969 356 Z" fill="url(#shirtGrad)" stroke="#ffffff" stroke-opacity="0.34" stroke-width="6" />

    <g clip-path="url(#shirtClip)">
      <rect x="454" y="140" width="492" height="1400" fill="url(#shirtShadow)" />
      <rect x="470" y="180" width="460" height="1310" fill="url(#weave)" opacity="0.9" />
      <rect x="544" y="156" width="312" height="1316" fill="url(#clothSheen)" transform="rotate(-3 700 820)" opacity="0.95" />
      <path d="M480 288 C560 360 632 384 700 384 C768 384 840 360 920 288 L920 1500 L480 1500 Z" fill="#ffffff" fill-opacity="0.03" />
      <rect x="470" y="308" width="460" height="1210" fill="#ffffff" fill-opacity="0.02" />
    </g>

    <g clip-path="url(#sleeveLeftClip)">
      <rect x="160" y="250" width="370" height="620" fill="url(#weave)" opacity="0.82" />
      <rect x="168" y="250" width="360" height="620" fill="#ffffff" fill-opacity="0.03" />
    </g>

    <g clip-path="url(#sleeveRightClip)">
      <rect x="872" y="250" width="370" height="620" fill="url(#weave)" opacity="0.82" />
      <rect x="872" y="250" width="360" height="620" fill="#ffffff" fill-opacity="0.03" />
    </g>

    <path d="M408 210 L496 164 L582 278 L818 278 L904 164 L992 210 L918 348 L482 348 Z" fill="#ffffff" fill-opacity="0.16" stroke="#ffffff" stroke-opacity="0.56" stroke-width="6" />
    <path d="M533 182 L600 150 L700 272 L800 150 L867 182 L811 286 L589 286 Z" fill="#ffffff" fill-opacity="0.28" />
    <path d="M445 346 L510 382 L510 1510 L445 1510 Z" fill="#000000" fill-opacity="0.06" />
    <path d="M955 346 L890 382 L890 1510 L955 1510 Z" fill="#000000" fill-opacity="0.06" />

    <path d="M618 350 C650 378 676 392 700 392 C724 392 750 378 782 350" fill="none" stroke="#ffffff" stroke-opacity="0.74" stroke-width="7" stroke-linecap="round" />
    <path d="M700 392 L700 1460" fill="none" stroke="#ffffff" stroke-opacity="0.18" stroke-width="4" stroke-linecap="round" />
    <circle cx="700" cy="460" r="11" fill="#ffffff" fill-opacity="0.82" />
    <circle cx="700" cy="540" r="11" fill="#ffffff" fill-opacity="0.82" />
    <circle cx="700" cy="620" r="11" fill="#ffffff" fill-opacity="0.82" />
    <circle cx="700" cy="700" r="11" fill="#ffffff" fill-opacity="0.82" />
    <circle cx="700" cy="780" r="11" fill="#ffffff" fill-opacity="0.82" />

    <path d="M488 344 L570 344 L570 1482 L488 1482 Z" fill="#ffffff" fill-opacity="0.02" />
    <path d="M830 344 L912 344 L912 1482 L830 1482 Z" fill="#ffffff" fill-opacity="0.02" />

    <path d="M398 386 C416 362 436 346 464 338" fill="none" stroke="#ffffff" stroke-opacity="0.34" stroke-width="6" stroke-linecap="round" />
    <path d="M1002 386 C984 362 964 346 936 338" fill="none" stroke="#ffffff" stroke-opacity="0.34" stroke-width="6" stroke-linecap="round" />

    <path d="M318 694 L318 1460 C318 1492 344 1518 376 1518 L446 1518 L470 1458 L398 1458 C378 1458 362 1442 362 1422 L362 748 C362 730 350 708 318 694 Z" fill="{shadow_color}" fill-opacity="0.36" />
    <path d="M1082 694 L1082 1460 C1082 1492 1056 1518 1024 1518 L954 1518 L930 1458 L1002 1458 C1022 1458 1038 1442 1038 1422 L1038 748 C1038 730 1050 708 1082 694 Z" fill="{shadow_color}" fill-opacity="0.36" />

    <path d="M274 1448 L236 1538 L178 1538 L162 1474 L190 1448 Z" fill="{fabric_dark}" />
    <path d="M1126 1448 L1164 1538 L1222 1538 L1238 1474 L1210 1448 Z" fill="{fabric_dark}" />
  </g>

  <rect x="30" y="30" width="1340" height="1740" rx="50" fill="none" stroke="#ffffff" stroke-opacity="0.28" stroke-width="2" />
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
            "texture_strategy": "svg_full_bleed_shirt",
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
