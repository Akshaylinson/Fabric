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
    AI_PROVIDER: str
    OPENAI_API_KEY: str
    OPENAI_MODEL: str
    OPENAI_MODEL_VERSION: str
    FASHN_API_KEY: str
    FAL_API_KEY: str
    FAL_MODEL: str
    REPLICATE_API_TOKEN: str
    REPLICATE_MODEL: str
    REPLICATE_MODEL_VERSION: str
    TRYON_OUTPUT_FORMAT: str
    TRYON_IMAGE_WIDTH: int
    TRYON_IMAGE_HEIGHT: int
    TRYON_VALIDATE_CUSTOMER_IMAGE: bool
    TRYON_VALIDATE_OUTPUT: bool
    TRYON_ENABLE_FACE_RESTORATION: bool
    TRYON_ENABLE_UPSCALING: bool


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings(
        AI_PROVIDER=os.getenv("AI_PROVIDER", "openai"),
        OPENAI_API_KEY=os.getenv("OPENAI_API_KEY", ""),
        OPENAI_MODEL=os.getenv("OPENAI_MODEL", "gpt-image-1"),
        OPENAI_MODEL_VERSION=os.getenv("OPENAI_MODEL_VERSION", "latest"),
        FASHN_API_KEY=os.getenv("FASHN_API_KEY", ""),
        FAL_API_KEY=os.getenv("FAL_API_KEY", ""),
        FAL_MODEL=os.getenv("FAL_MODEL", "kolors-virtual-tryon"),
        REPLICATE_API_TOKEN=os.getenv("REPLICATE_API_TOKEN", ""),
        REPLICATE_MODEL=os.getenv("REPLICATE_MODEL", "catvton"),
        REPLICATE_MODEL_VERSION=os.getenv("REPLICATE_MODEL_VERSION", ""),
        TRYON_OUTPUT_FORMAT=os.getenv("TRYON_OUTPUT_FORMAT", "svg"),
        TRYON_IMAGE_WIDTH=_get_int("TRYON_IMAGE_WIDTH", 1200),
        TRYON_IMAGE_HEIGHT=_get_int("TRYON_IMAGE_HEIGHT", 1600),
        TRYON_VALIDATE_CUSTOMER_IMAGE=_get_bool("TRYON_VALIDATE_CUSTOMER_IMAGE", True),
        TRYON_VALIDATE_OUTPUT=_get_bool("TRYON_VALIDATE_OUTPUT", True),
        TRYON_ENABLE_FACE_RESTORATION=_get_bool("TRYON_ENABLE_FACE_RESTORATION", False),
        TRYON_ENABLE_UPSCALING=_get_bool("TRYON_ENABLE_UPSCALING", False),
    )


settings = get_settings()
