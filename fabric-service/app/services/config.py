from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import os


def _get_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    return int(value)


def _get_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    TEMPLATE_SERVICE_URL: str
    OPENROUTER_API_KEY: str
    OPENROUTER_BASE_URL: str
    OPENROUTER_IMAGE_ENDPOINT: str
    OPENROUTER_MODEL: str
    OPENROUTER_TIMEOUT: int
    OPENROUTER_REFERER: str
    OPENROUTER_TITLE: str
    RENDER_OUTPUT_FORMAT: str
    RENDER_IMAGE_COUNT: int
    RENDER_USE_SEED: bool
    RENDER_SEED: int
    RENDER_MAX_REFERENCES: int
    RENDER_IMAGE_WIDTH: int
    RENDER_IMAGE_HEIGHT: int


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings(
        TEMPLATE_SERVICE_URL=os.getenv("TEMPLATE_SERVICE_URL", "http://template-service:8001"),
        OPENROUTER_API_KEY=os.getenv("OPENROUTER_API_KEY", ""),
        OPENROUTER_BASE_URL=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
        OPENROUTER_IMAGE_ENDPOINT=os.getenv("OPENROUTER_IMAGE_ENDPOINT", "/images"),
        OPENROUTER_MODEL=os.getenv("OPENROUTER_MODEL", "black-forest-labs/flux.2-flex"),
        OPENROUTER_TIMEOUT=_get_int("OPENROUTER_TIMEOUT", 180),
        OPENROUTER_REFERER=os.getenv("OPENROUTER_REFERER", "http://localhost:3000"),
        OPENROUTER_TITLE=os.getenv("OPENROUTER_TITLE", "Textile AI Platform"),
        RENDER_OUTPUT_FORMAT=os.getenv("RENDER_OUTPUT_FORMAT", "png"),
        RENDER_IMAGE_COUNT=_get_int("RENDER_IMAGE_COUNT", 1),
        RENDER_USE_SEED=_get_bool("RENDER_USE_SEED", False),
        RENDER_SEED=_get_int("RENDER_SEED", 42),
        RENDER_MAX_REFERENCES=_get_int("RENDER_MAX_REFERENCES", 4),
        RENDER_IMAGE_WIDTH=_get_int("RENDER_IMAGE_WIDTH", 1024),
        RENDER_IMAGE_HEIGHT=_get_int("RENDER_IMAGE_HEIGHT", 1024),
    )


settings = get_settings()

