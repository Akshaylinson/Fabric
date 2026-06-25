from __future__ import annotations

import base64
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
import urllib.request


def _extract_b64_image(response_json: dict[str, Any]) -> str | None:
    data = response_json.get("data")
    if isinstance(data, list) and data:
        first = data[0]
        if isinstance(first, dict):
            if first.get("b64_json"):
                return str(first["b64_json"])
            if first.get("image"):
                return str(first["image"])

    images = response_json.get("images")
    if isinstance(images, list) and images:
        first = images[0]
        if isinstance(first, dict) and first.get("b64_json"):
            return str(first["b64_json"])

    output = response_json.get("output")
    if isinstance(output, list) and output:
        first = output[0]
        if isinstance(first, dict) and first.get("b64_json"):
            return str(first["b64_json"])

    return None


def _download_image(url: str) -> bytes:
    with urllib.request.urlopen(url) as response:  # nosec B310 - provider-controlled URL
        return response.read()


def decode_and_save(response_json: dict[str, Any], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    image_data = _extract_b64_image(response_json)
    if image_data:
        image_bytes = base64.b64decode(image_data)
        path.write_bytes(image_bytes)
        return path

    url_candidates = []
    data = response_json.get("data")
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and item.get("url"):
                url_candidates.append(str(item["url"]))
    if response_json.get("url"):
        url_candidates.append(str(response_json["url"]))

    for candidate in url_candidates:
        parsed = urlparse(candidate)
        if parsed.scheme in {"http", "https", "file"}:
            path.write_bytes(_download_image(candidate))
            return path

    raise ValueError("OpenRouter response did not include an image payload")

