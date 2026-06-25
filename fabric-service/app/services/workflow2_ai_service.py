from __future__ import annotations

import hashlib
import io
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Any
from uuid import uuid4

from PIL import Image

from app.services.config import get_settings
from app.services.image_decoder import decode_and_save
from app.services.openrouter_client import OpenRouterClient
from app.services.prompt_builder import build_prompt
from app.services.reference_builder import build_reference_manifest, build_references
from textile_shared.persistence import LocalObjectStorage, service_object_dir


@dataclass(frozen=True)
class Workflow2RenderResult:
    render_id: str
    image_path: str
    image_url: str
    rendered_image_ref: str
    provider: str
    model: str
    prompt: str
    metadata: dict[str, Any]
    processing_logs: list[dict[str, str]]
    timing: dict[str, Any]
    notes: str
    reference_manifest: list[dict[str, str]]
    response_json: dict[str, Any]


class Workflow2AIService:
    def __init__(
        self,
        storage: LocalObjectStorage | None = None,
        client: OpenRouterClient | None = None,
    ) -> None:
        self.settings = get_settings()
        self.storage = storage or LocalObjectStorage(service_object_dir("fabric-service"))
        self.client = client or OpenRouterClient(self.settings)

    def _fabric_extension(self, fabric_bytes: bytes, fabric_mime_type: str | None) -> str:
        if fabric_mime_type:
            return fabric_mime_type.split("/")[-1].replace("jpeg", "jpg")

        try:
            image = Image.open(io.BytesIO(fabric_bytes))
            return (image.format or "png").lower().replace("jpeg", "jpg")
        except Exception:
            return "png"

    def _fabric_color_hint(self, fabric_bytes: bytes) -> str:
        try:
            image = Image.open(io.BytesIO(fabric_bytes)).convert("RGBA")
            image.thumbnail((48, 48))
            pixels = list(image.getdata())
            if not pixels:
                raise ValueError("empty image")

            red = green = blue = total = 0.0
            for r, g, b, a in pixels:
                weight = a / 255 if a else 0.0
                red += r * weight
                green += g * weight
                blue += b * weight
                total += weight

            if total <= 0:
                raise ValueError("fully transparent")

            return f"#{int(red / total):02x}{int(green / total):02x}{int(blue / total):02x}"
        except Exception:
            digest = hashlib.sha256(fabric_bytes).hexdigest()
            return f"#{digest[0:6]}"

    def render(
        self,
        *,
        template_package: dict[str, Any],
        fabric_ref: str,
        fabric_bytes: bytes,
        fabric_mime_type: str | None = None,
        render_id: str | None = None,
        render_label: str | None = None,
    ) -> Workflow2RenderResult:
        started_at = datetime.now(timezone.utc)
        timer_started = perf_counter()
        render_id = render_id or f"rnd_{uuid4().hex[:12]}"

        processing_logs: list[dict[str, str]] = [
            {
                "timestamp": started_at.isoformat(),
                "stage": "fabric-ingestion",
                "message": f"Received uploaded fabric {fabric_ref} for AI rendering.",
            },
        ]

        extension = self._fabric_extension(fabric_bytes, fabric_mime_type)
        fabric_source_ref = self.storage.put_bytes(f"fabrics/{fabric_ref}/source/fabric.{extension}", fabric_bytes)

        reference_manifest = build_reference_manifest(template_package, fabric_bytes, fabric_mime_type)
        references = [item.data_url for item in reference_manifest]
        prompt = build_prompt()
        processing_logs.append(
            {
                "timestamp": started_at.isoformat(),
                "stage": "reference-preparation",
                "message": f"Prepared {len(references)} reference images for OpenRouter FLUX.",
            }
        )

        processing_logs.append(
            {
                "timestamp": started_at.isoformat(),
                "stage": "prompt-build",
                "message": "Built the FLUX garment-preservation prompt.",
            }
        )

        response_json = self.client.generate_image(prompt, references)
        processing_logs.append(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "stage": "openrouter-response",
                "message": "OpenRouter returned an image payload.",
            }
        )

        final_path = decode_and_save(response_json, self.storage.path_for(f"renders/{render_id}/final.png"))
        final_bytes = Path(final_path).read_bytes()
        rendered_alias_ref = self.storage.put_bytes(f"renders/{render_id}/rendered.png", final_bytes)
        rendered_image_ref = final_path.as_uri()

        completed_at = datetime.now(timezone.utc)
        processing_time_ms = round((perf_counter() - timer_started) * 1000, 2)
        provider = "openrouter"
        model = self.settings.OPENROUTER_MODEL
        fabric_color_hint = self._fabric_color_hint(fabric_bytes)

        metadata: dict[str, Any] = {
            "provider": provider,
            "model": model,
            "template_id": template_package.get("template_id"),
            "template_name": template_package.get("template_name"),
            "template_preview_image": template_package.get("preview_image"),
            "fabric_ref": fabric_ref,
            "fabric_source_ref": fabric_source_ref,
            "fabric_color_hint": fabric_color_hint,
            "reference_count": len(references),
            "reference_roles": [item.role for item in reference_manifest],
            "reference_sources": [item.source_ref for item in reference_manifest],
            "reference_manifest": [
                {"role": item.role, "source_ref": item.source_ref, "mime_type": item.mime_type}
                for item in reference_manifest
            ],
            "render_output_format": self.settings.RENDER_OUTPUT_FORMAT,
            "render_image_count": self.settings.RENDER_IMAGE_COUNT,
            "render_use_seed": self.settings.RENDER_USE_SEED,
            "render_seed": self.settings.RENDER_SEED if self.settings.RENDER_USE_SEED else None,
            "image_width": self.settings.RENDER_IMAGE_WIDTH,
            "image_height": self.settings.RENDER_IMAGE_HEIGHT,
            "preserved_structure": True,
            "fabric_fit": "applied",
            "texture_strategy": "openrouter_flux_ai",
            "garment_area_covered": "template-guided",
        }

        processing_logs.append(
            {
                "timestamp": completed_at.isoformat(),
                "stage": "render-complete",
                "message": f"Render {render_id} completed in {processing_time_ms} ms.",
            }
        )

        timing = {
            "started_at": started_at.isoformat(),
            "completed_at": completed_at.isoformat(),
            "processing_time_ms": processing_time_ms,
        }

        image_url = f"/renders/{render_id}/image"
        notes = "OpenRouter FLUX render completed successfully."

        package = {
            "render_id": render_id,
            "status": "completed",
            "provider": provider,
            "model": model,
            "prompt": prompt,
            "image_url": image_url,
            "image_path": rendered_image_ref,
            "rendered_image_ref": rendered_image_ref,
            "rendered_alias_ref": rendered_alias_ref,
            "fabric_source_ref": fabric_source_ref,
            "metadata": metadata,
            "processing_logs": processing_logs,
            "timing": timing,
            "notes": notes,
            "response_json": response_json,
            "render_label": render_label or f"Fabric Render for {template_package.get('template_id', 'template')}",
        }

        self.storage.put_json(f"renders/{render_id}/metadata.json", metadata)
        self.storage.put_json(f"renders/{render_id}/logs.json", processing_logs)
        self.storage.put_json(f"renders/{render_id}/package.json", package)
        self.storage.put_json(f"renders/{render_id}/response.json", response_json)

        return Workflow2RenderResult(
            render_id=render_id,
            image_path=rendered_image_ref,
            image_url=image_url,
            rendered_image_ref=rendered_image_ref,
            provider=provider,
            model=model,
            prompt=prompt,
            metadata=metadata,
            processing_logs=processing_logs,
            timing=timing,
            notes=notes,
            reference_manifest=[
                {"role": item.role, "source_ref": item.source_ref, "mime_type": item.mime_type, "data_url": item.data_url}
                for item in reference_manifest
            ],
            response_json=response_json,
        )

