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
    # Primary provider
    PRIMARY_RENDER_PROVIDER: str
    PRIMARY_RENDER_API_KEY: str
    PRIMARY_RENDER_BASE_URL: str
    PRIMARY_RENDER_ENDPOINT: str
    PRIMARY_RENDER_MODEL: str
    PRIMARY_RENDER_TIMEOUT: int
    PRIMARY_RENDER_REFERER: str   # used when provider == openrouter
    PRIMARY_RENDER_TITLE: str     # used when provider == openrouter
    # Secondary / fallback provider
    SECONDARY_RENDER_PROVIDER: str
    SECONDARY_RENDER_API_KEY: str
    SECONDARY_RENDER_BASE_URL: str
    SECONDARY_RENDER_ENDPOINT: str
    SECONDARY_RENDER_MODEL: str
    SECONDARY_RENDER_TIMEOUT: int
    # Shared render settings
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
        PRIMARY_RENDER_PROVIDER=os.getenv("PRIMARY_RENDER_PROVIDER", "openrouter"),
        PRIMARY_RENDER_API_KEY=os.getenv("PRIMARY_RENDER_API_KEY", ""),
        PRIMARY_RENDER_BASE_URL=os.getenv("PRIMARY_RENDER_BASE_URL", "https://openrouter.ai/api/v1"),
        PRIMARY_RENDER_ENDPOINT=os.getenv("PRIMARY_RENDER_ENDPOINT", "/images"),
        PRIMARY_RENDER_MODEL=os.getenv("PRIMARY_RENDER_MODEL", "black-forest-labs/flux.2-flex"),
        PRIMARY_RENDER_TIMEOUT=_get_int("PRIMARY_RENDER_TIMEOUT", 180),
        PRIMARY_RENDER_REFERER=os.getenv("PRIMARY_RENDER_REFERER", "http://localhost:3000"),
        PRIMARY_RENDER_TITLE=os.getenv("PRIMARY_RENDER_TITLE", "Tailoring AI Platform"),
        SECONDARY_RENDER_PROVIDER=os.getenv("SECONDARY_RENDER_PROVIDER", ""),
        SECONDARY_RENDER_API_KEY=os.getenv("SECONDARY_RENDER_API_KEY", ""),
        SECONDARY_RENDER_BASE_URL=os.getenv("SECONDARY_RENDER_BASE_URL", ""),
        SECONDARY_RENDER_ENDPOINT=os.getenv("SECONDARY_RENDER_ENDPOINT", "/images/generations"),
        SECONDARY_RENDER_MODEL=os.getenv("SECONDARY_RENDER_MODEL", ""),
        SECONDARY_RENDER_TIMEOUT=_get_int("SECONDARY_RENDER_TIMEOUT", 180),
        RENDER_OUTPUT_FORMAT=os.getenv("RENDER_OUTPUT_FORMAT", "png"),
        RENDER_IMAGE_COUNT=_get_int("RENDER_IMAGE_COUNT", 1),
        RENDER_USE_SEED=_get_bool("RENDER_USE_SEED", False),
        RENDER_SEED=_get_int("RENDER_SEED", 42),
        RENDER_MAX_REFERENCES=_get_int("RENDER_MAX_REFERENCES", 4),
        RENDER_IMAGE_WIDTH=_get_int("RENDER_IMAGE_WIDTH", 1024),
        RENDER_IMAGE_HEIGHT=_get_int("RENDER_IMAGE_HEIGHT", 1024),
    )


settings = get_settings()

