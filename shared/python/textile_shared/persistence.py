from __future__ import annotations

import base64
import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


def storage_root() -> Path:
    root = os.getenv("TEXTILE_STORAGE_ROOT", "/data")
    return Path(root).resolve()


def ensure_directory(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def service_state_dir(service_name: str) -> Path:
    return ensure_directory(storage_root() / "state" / service_name)


def service_object_dir(service_name: str) -> Path:
    return ensure_directory(storage_root() / "objects" / service_name)


def _atomic_write(path: Path, payload: bytes) -> None:
    ensure_directory(path.parent)
    with tempfile.NamedTemporaryFile(delete=False, dir=path.parent) as handle:
        handle.write(payload)
        temp_name = handle.name
    os.replace(temp_name, path)


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    _atomic_write(path, json.dumps(value, indent=2, sort_keys=True).encode("utf-8"))


def decode_data_url(data_url: str) -> tuple[bytes, str | None]:
    if "," not in data_url:
        return base64.b64decode(data_url), None

    header, encoded = data_url.split(",", 1)
    mime_type = None
    if header.startswith("data:"):
        mime_type = header[5:].split(";", 1)[0] or None
    if ";base64" in header:
        return base64.b64decode(encoded), mime_type
    return encoded.encode("utf-8"), mime_type


@dataclass
class PersistentJsonStore:
    path: Path
    default_factory: Callable[[], Any] = dict

    def load(self) -> Any:
        return read_json(self.path, self.default_factory())

    def save(self, value: Any) -> Any:
        write_json(self.path, value)
        return value

    def update(self, mutator: Callable[[Any], Any]) -> Any:
        current = self.load()
        updated = mutator(current)
        self.save(updated)
        return updated


class LocalObjectStorage:
    def __init__(self, root: Path):
        self.root = ensure_directory(root)

    def path_for(self, key: str) -> Path:
        return self.root / key

    def put_bytes(self, key: str, payload: bytes) -> str:
        path = self.path_for(key)
        _atomic_write(path, payload)
        return path.as_uri()

    def put_text(self, key: str, payload: str) -> str:
        return self.put_bytes(key, payload.encode("utf-8"))

    def put_json(self, key: str, payload: Any) -> str:
        return self.put_text(key, json.dumps(payload, indent=2, sort_keys=True))

    def exists(self, key: str) -> bool:
        return self.path_for(key).exists()

    def read_json(self, key: str, default: Any = None) -> Any:
        return read_json(self.path_for(key), default)

