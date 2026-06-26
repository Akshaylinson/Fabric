from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from app.services.config import Settings


@dataclass(frozen=True)
class TryOnGenerationResult:
    preview_id: str
    provider: str
    model: str
    model_version: str | None
    image_url: str
    response_json: dict[str, Any]


class BaseTryOnProvider:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    @property
    def provider_name(self) -> str:
        raise NotImplementedError

    @property
    def model_name(self) -> str:
        raise NotImplementedError

    @property
    def model_version(self) -> str | None:
        return None

    def generate(self, prompt: str, customer_image_ref: str, garment_image_ref: str) -> TryOnGenerationResult:
        preview_id = f"pre_{uuid4().hex[:12]}"
        response_json = {
            "id": preview_id,
            "provider": self.provider_name,
            "model": self.model_name,
            "model_version": self.model_version,
            "prompt": prompt,
            "customer_image_ref": customer_image_ref,
            "garment_image_ref": garment_image_ref,
            "data": [],
        }
        return TryOnGenerationResult(
            preview_id=preview_id,
            provider=self.provider_name,
            model=self.model_name,
            model_version=self.model_version,
            image_url=f"/tryon/render/{preview_id}/image",
            response_json=response_json,
        )


class OpenAIProvider(BaseTryOnProvider):
    @property
    def provider_name(self) -> str:
        return "openai"

    @property
    def model_name(self) -> str:
        return self.settings.OPENAI_MODEL

    @property
    def model_version(self) -> str | None:
        return self.settings.OPENAI_MODEL_VERSION


class FashnProvider(BaseTryOnProvider):
    @property
    def provider_name(self) -> str:
        return "fashn"

    @property
    def model_name(self) -> str:
        return "fashn-virtual-tryon"


class FalProvider(BaseTryOnProvider):
    @property
    def provider_name(self) -> str:
        return "fal"

    @property
    def model_name(self) -> str:
        return self.settings.FAL_MODEL


class ReplicateProvider(BaseTryOnProvider):
    @property
    def provider_name(self) -> str:
        return "replicate"

    @property
    def model_name(self) -> str:
        return self.settings.REPLICATE_MODEL

    @property
    def model_version(self) -> str | None:
        return self.settings.REPLICATE_MODEL_VERSION or None


def build_provider(settings: Settings) -> BaseTryOnProvider:
    provider = settings.AI_PROVIDER.strip().lower()
    if provider == "fashn":
        return FashnProvider(settings)
    if provider == "fal":
        return FalProvider(settings)
    if provider == "replicate":
        return ReplicateProvider(settings)
    return OpenAIProvider(settings)
