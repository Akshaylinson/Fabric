from __future__ import annotations

from dataclasses import dataclass
from time import sleep
from typing import Any

import requests

from app.services.config import Settings, get_settings


@dataclass(frozen=True)
class OpenRouterError(RuntimeError):
    message: str
    status_code: int | None = None

    def __str__(self) -> str:  # pragma: no cover - simple wrapper
        suffix = f" (status {self.status_code})" if self.status_code is not None else ""
        return f"{self.message}{suffix}"


class OpenRouterClient:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()
        self.session = requests.Session()

    def _request_headers(self) -> dict[str, str]:
        if not self.settings.OPENROUTER_API_KEY:
            raise OpenRouterError("Missing OpenRouter API key")

        return {
            "Authorization": f"Bearer {self.settings.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": self.settings.OPENROUTER_REFERER,
            "X-Title": self.settings.OPENROUTER_TITLE,
        }

    def generate_image(self, prompt: str, references: list[str]) -> dict[str, Any]:
        url = f"{self.settings.OPENROUTER_BASE_URL.rstrip('/')}/{self.settings.OPENROUTER_IMAGE_ENDPOINT.lstrip('/')}"
        payload: dict[str, Any] = {
            "model": self.settings.OPENROUTER_MODEL,
            "prompt": prompt,
            "input_references": references[: self.settings.RENDER_MAX_REFERENCES],
            "output_format": self.settings.RENDER_OUTPUT_FORMAT,
            "n": self.settings.RENDER_IMAGE_COUNT,
        }

        if self.settings.RENDER_USE_SEED:
            payload["seed"] = self.settings.RENDER_SEED

        last_error: str | None = None
        for attempt in range(3):
            try:
                response = self.session.post(
                    url,
                    headers=self._request_headers(),
                    json=payload,
                    timeout=self.settings.OPENROUTER_TIMEOUT,
                )
                if response.status_code >= 400:
                    raise OpenRouterError(response.text or "OpenRouter request failed", response.status_code)
                return response.json()
            except (requests.RequestException, ValueError, OpenRouterError) as exc:
                last_error = str(exc)
                if attempt == 2:
                    raise OpenRouterError(last_error) from exc
                sleep(0.75 * (attempt + 1))

        raise OpenRouterError(last_error or "OpenRouter request failed")

