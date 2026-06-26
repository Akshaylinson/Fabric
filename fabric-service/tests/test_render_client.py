from __future__ import annotations

from unittest import TestCase
from unittest.mock import patch

from app.services.config import Settings
from app.services.render_client import GenericRenderAdapter, _ProviderConfig


class _FakeResponse:
    status_code = 200

    def json(self) -> dict[str, str]:
        return {"ok": "true"}


class RenderClientTests(TestCase):
    def _settings(self, max_references: int = 2) -> Settings:
        return Settings(
            TEMPLATE_SERVICE_URL="http://template-service:8001",
            PRIMARY_RENDER_PROVIDER="openrouter",
            PRIMARY_RENDER_API_KEY="primary-key",
            PRIMARY_RENDER_BASE_URL="https://openrouter.ai/api/v1",
            PRIMARY_RENDER_ENDPOINT="/images",
            PRIMARY_RENDER_MODEL="black-forest-labs/flux.2-flex",
            PRIMARY_RENDER_TIMEOUT=30,
            PRIMARY_RENDER_REFERER="http://localhost:3000",
            PRIMARY_RENDER_TITLE="Tailoring AI Platform",
            SECONDARY_RENDER_PROVIDER="",
            SECONDARY_RENDER_API_KEY="",
            SECONDARY_RENDER_BASE_URL="",
            SECONDARY_RENDER_ENDPOINT="/images/generations",
            SECONDARY_RENDER_MODEL="",
            SECONDARY_RENDER_TIMEOUT=30,
            RENDER_OUTPUT_FORMAT="png",
            RENDER_IMAGE_COUNT=1,
            RENDER_USE_SEED=False,
            RENDER_SEED=42,
            RENDER_MAX_REFERENCES=max_references,
            RENDER_IMAGE_WIDTH=1024,
            RENDER_IMAGE_HEIGHT=1024,
        )

    def test_openrouter_wraps_input_references_as_objects(self) -> None:
        adapter = GenericRenderAdapter(
            _ProviderConfig(
                provider="openrouter",
                api_key="test-key",
                base_url="https://openrouter.ai/api/v1",
                endpoint="/images",
                model="black-forest-labs/flux.2-flex",
                timeout=30,
                referer="http://localhost:3000",
                title="Tailoring AI Platform",
            ),
            self._settings(max_references=2),
        )

        with patch("app.services.render_client.requests.post", return_value=_FakeResponse()) as mock_post:
            adapter.generate_image("render a shirt", ["data:one", "data:two", "data:three"])

        payload = mock_post.call_args.kwargs["json"]
        headers = mock_post.call_args.kwargs["headers"]

        self.assertEqual(
            payload["input_references"],
            [
                {"type": "image_url", "image_url": {"url": "data:one"}},
                {"type": "image_url", "image_url": {"url": "data:two"}},
            ],
        )
        self.assertEqual(headers["HTTP-Referer"], "http://localhost:3000")
        self.assertEqual(headers["X-OpenRouter-Title"], "Tailoring AI Platform")
        self.assertNotIn("X-Title", headers)

    def test_non_openrouter_keeps_reference_strings(self) -> None:
        adapter = GenericRenderAdapter(
            _ProviderConfig(
                provider="together",
                api_key="test-key",
                base_url="https://api.together.xyz",
                endpoint="/images/generations",
                model="flux",
                timeout=30,
            ),
            self._settings(max_references=1),
        )

        with patch("app.services.render_client.requests.post", return_value=_FakeResponse()) as mock_post:
            adapter.generate_image("render a shirt", ["data:one", "data:two"])

        payload = mock_post.call_args.kwargs["json"]
        headers = mock_post.call_args.kwargs["headers"]

        self.assertEqual(payload["input_references"], ["data:one"])
        self.assertNotIn("HTTP-Referer", headers)
        self.assertNotIn("X-OpenRouter-Title", headers)

