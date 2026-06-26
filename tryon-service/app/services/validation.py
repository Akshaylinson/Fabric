from __future__ import annotations

from pathlib import Path
from typing import Any

from textile_shared.persistence import read_json, service_object_dir


def _customer_hint(customer_ref: str, customer_bytes: bytes | None = None) -> str:
    ref = customer_ref.lower()
    if "group" in ref or "crowd" in ref:
        return "Customer image appears to include multiple people."
    if "blur" in ref or "lowres" in ref:
        return "Customer image appears to be blurry or low resolution."
    if "side" in ref or "back" in ref:
        return "Front-facing customer image is preferred for identity preservation."
    if customer_bytes is not None and len(customer_bytes) < 4_000:
        return "Customer image payload is too small to be reliable."
    return ""


def validate_customer_image(customer_ref: str, customer_bytes: bytes | None = None) -> dict[str, Any]:
    reason = _customer_hint(customer_ref, customer_bytes)
    return {"valid": reason == "", "reason": reason}


def load_garment_summary(render_id: str) -> dict[str, Any]:
    package_path = service_object_dir("fabric-service") / "renders" / render_id / "package.json"
    package = read_json(package_path, default={})
    if not isinstance(package, dict):
        package = {}

    metadata = package.get("metadata", {}) if isinstance(package.get("metadata"), dict) else {}
    return {
        "render_id": render_id,
        "rendered_image_ref": package.get("rendered_image_ref"),
        "provider": package.get("provider", metadata.get("provider", "")),
        "model": package.get("model", metadata.get("model", "")),
        "fabric": metadata.get("fabric_color_hint", metadata.get("fabric_fit", "unknown fabric")),
        "color": metadata.get("fabric_color_hint", "preserve rendered colour"),
        "notes": package.get("notes", "Workflow 2 rendered garment reference."),
        "metadata": metadata,
        "exists": package_path.exists(),
    }


def validate_garment_summary(garment_summary: dict[str, Any]) -> dict[str, Any]:
    if garment_summary.get("exists"):
        return {"valid": True, "reason": ""}
    return {"valid": False, "reason": f"Workflow 2 render '{garment_summary.get('render_id')}' was not found."}


def validate_output(render_path: Path, garment_summary: dict[str, Any]) -> dict[str, Any]:
    if not render_path.exists():
        return {"valid": False, "reason": "Generated preview was not stored."}
    if not garment_summary.get("exists"):
        return {"valid": False, "reason": "Garment reference could not be loaded."}
    return {"valid": True, "reason": ""}
