from __future__ import annotations

import base64
import mimetypes
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse, unquote
import urllib.request


@dataclass(frozen=True)
class ReferenceImage:
    role: str
    source_ref: str
    mime_type: str | None
    data_url: str


def _guess_mime_type(source_ref: str, fallback: str | None = None) -> str:
    guessed, _encoding = mimetypes.guess_type(source_ref)
    return guessed or fallback or "application/octet-stream"


def _read_source_bytes(source_ref: str) -> tuple[bytes, str | None]:
    parsed = urlparse(source_ref)
    if parsed.scheme in {"http", "https", "file"}:
        with urllib.request.urlopen(source_ref) as response:  # nosec B310 - trusted local/file or configured service URL
            payload = response.read()
            mime_type = response.headers.get_content_type() if hasattr(response, "headers") else None
            return payload, mime_type

    path = Path(unquote(source_ref))
    if path.exists():
        return path.read_bytes(), _guess_mime_type(str(path))

    raise FileNotFoundError(f"Unable to load reference image from {source_ref}")


def _to_data_url(raw_bytes: bytes, mime_type: str | None) -> str:
    encoded = base64.b64encode(raw_bytes).decode("ascii")
    return f"data:{mime_type or 'application/octet-stream'};base64,{encoded}"


def _source_uri_from_template(template_package: dict[str, Any], role: str) -> str | None:
    source_images = template_package.get("source_images") or {}
    if isinstance(source_images, dict):
        source = source_images.get(role) or {}
        if isinstance(source, dict):
            storage_uri = source.get("storage_uri")
            if storage_uri:
                return str(storage_uri)

    storage = template_package.get("storage") or {}
    preview_image = storage.get("preview_image") or template_package.get("preview_image")
    if role == "front" and preview_image:
        return str(preview_image)
    return None


def build_reference_manifest(
    template_package: dict[str, Any],
    fabric_bytes: bytes,
    fabric_mime_type: str | None = None,
) -> list[ReferenceImage]:
    roles = ["front", "side", "back"]
    manifest: list[ReferenceImage] = []

    for role in roles:
        source_ref = _source_uri_from_template(template_package, role)
        if not source_ref:
            continue
        raw_bytes, mime_type = _read_source_bytes(source_ref)
        manifest.append(
            ReferenceImage(
                role=role,
                source_ref=source_ref,
                mime_type=mime_type,
                data_url=_to_data_url(raw_bytes, mime_type),
            )
        )

    manifest.append(
        ReferenceImage(
            role="fabric",
            source_ref="uploaded-fabric",
            mime_type=fabric_mime_type,
            data_url=_to_data_url(fabric_bytes, fabric_mime_type or "image/png"),
        )
    )

    return manifest[:4]


def build_references(
    template_package: dict[str, Any],
    fabric_bytes: bytes,
    fabric_mime_type: str | None = None,
) -> list[str]:
    return [item.data_url for item in build_reference_manifest(template_package, fabric_bytes, fabric_mime_type)]

