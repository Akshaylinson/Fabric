from __future__ import annotations

from time import sleep
from typing import Any, Protocol

import requests

from app.services.config import Settings, get_settings


class RenderClientError(RuntimeError):
    def __init__(self, message: str, status_code: int | None = None, provider: str = "unknown") -> None:
        super().__init__(message)
        self.status_code = status_code
        self.provider = provider

    def __str__(self) -> str:
        suffix = f" (status {self.status_code})" if self.status_code is not None else ""
        return f"[{self.provider}] {super().__str__()}{suffix}"


class RenderClientProtocol(Protocol):
    provider_name: str

    def generate_image(self, prompt: str, references: list[str]) -> dict[str, Any]: ...


class _ProviderConfig:
    """Holds resolved config for one provider slot (primary or secondary)."""

    def __init__(
        self,
        provider: str,
        api_key: str,
        base_url: str,
        endpoint: str,
        model: str,
        timeout: int,
        referer: str = "",
        title: str = "",
    ) -> None:
        self.provider = provider
        self.api_key = api_key
        self.base_url = base_url
        self.endpoint = endpoint
        self.model = model
        self.timeout = timeout
        self.referer = referer
        self.title = title


class GenericRenderAdapter:
    """
    Single adapter covering all providers:
      openrouter, gemini, flux, together, replicate, stability, or any
      OpenAI-compatible image generation endpoint.

    When provider == 'openrouter', the optional HTTP-Referer / X-OpenRouter-Title
    headers are added automatically.
    """

    def __init__(self, cfg: _ProviderConfig, settings: Settings) -> None:
        self._cfg = cfg
        self._settings = settings
        self._session = requests.Session()

    @property
    def provider_name(self) -> str:
        return self._cfg.provider

    def generate_image(self, prompt: str, references: list[str]) -> dict[str, Any]:
        if not self._cfg.api_key:
            raise RenderClientError(
                f"Missing API key for provider '{self._cfg.provider}'",
                provider=self._cfg.provider,
            )

        url = f"{self._cfg.base_url.rstrip('/')}/{self._cfg.endpoint.lstrip('/')}"

        headers: dict[str, str] = {
            "Authorization": f"Bearer {self._cfg.api_key}",
            "Content-Type": "application/json",
        }
        if self._cfg.provider.lower() == "openrouter":
            if self._cfg.referer:
                headers["HTTP-Referer"] = self._cfg.referer
            if self._cfg.title:
                headers["X-OpenRouter-Title"] = self._cfg.title

        input_references: list[Any]
        if self._cfg.provider.lower() == "openrouter":
            input_references = [
                {"type": "image_url", "image_url": {"url": reference}}
                for reference in references[: self._settings.RENDER_MAX_REFERENCES]
            ]
        else:
            input_references = references[: self._settings.RENDER_MAX_REFERENCES]

        payload: dict[str, Any] = {
            "model": self._cfg.model,
            "prompt": prompt,
            "input_references": input_references,
            "output_format": self._settings.RENDER_OUTPUT_FORMAT,
            "n": self._settings.RENDER_IMAGE_COUNT,
        }
        if self._settings.RENDER_USE_SEED:
            payload["seed"] = self._settings.RENDER_SEED

        return _post_with_retry(url, headers, payload, self._cfg.timeout, self._cfg.provider)


def _post_with_retry(
    url: str,
    headers: dict[str, str],
    payload: dict[str, Any],
    timeout: int,
    provider: str,
    max_attempts: int = 3,
) -> dict[str, Any]:
    last_error: str = "unknown error"
    for attempt in range(max_attempts):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=timeout)
            if response.status_code >= 400:
                raise RenderClientError(
                    response.text or "request failed",
                    status_code=response.status_code,
                    provider=provider,
                )
            return response.json()
        except (requests.RequestException, ValueError) as exc:
            last_error = str(exc)
            if attempt == max_attempts - 1:
                raise RenderClientError(last_error, provider=provider) from exc
            sleep(0.75 * (attempt + 1))
        except RenderClientError:
            if attempt == max_attempts - 1:
                raise
            sleep(0.75 * (attempt + 1))

    raise RenderClientError(last_error, provider=provider)


def build_primary_client(settings: Settings | None = None) -> RenderClientProtocol:
    s = settings or get_settings()
    cfg = _ProviderConfig(
        provider=s.PRIMARY_RENDER_PROVIDER,
        api_key=s.PRIMARY_RENDER_API_KEY,
        base_url=s.PRIMARY_RENDER_BASE_URL,
        endpoint=s.PRIMARY_RENDER_ENDPOINT,
        model=s.PRIMARY_RENDER_MODEL,
        timeout=s.PRIMARY_RENDER_TIMEOUT,
        referer=s.PRIMARY_RENDER_REFERER,
        title=s.PRIMARY_RENDER_TITLE,
    )
    return GenericRenderAdapter(cfg, s)


def build_secondary_client(settings: Settings | None = None) -> RenderClientProtocol | None:
    s = settings or get_settings()
    if not s.SECONDARY_RENDER_PROVIDER or not s.SECONDARY_RENDER_API_KEY:
        return None
    cfg = _ProviderConfig(
        provider=s.SECONDARY_RENDER_PROVIDER,
        api_key=s.SECONDARY_RENDER_API_KEY,
        base_url=s.SECONDARY_RENDER_BASE_URL,
        endpoint=s.SECONDARY_RENDER_ENDPOINT,
        model=s.SECONDARY_RENDER_MODEL,
        timeout=s.SECONDARY_RENDER_TIMEOUT,
    )
    return GenericRenderAdapter(cfg, s)


