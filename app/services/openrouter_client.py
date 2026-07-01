from typing import Any

import httpx

from app.core.config import settings
from app.core.errors import ExternalServiceError


class OpenRouterClient:
    """Thin async client for the OpenRouter chat completions API.

    Knows nothing about users or the database — only how to talk to OpenRouter.
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        site_url: str | None = None,
        app_name: str | None = None,
    ) -> None:
        self._api_key = api_key or settings.openrouter_api_key
        self._base_url = (base_url or settings.openrouter_base_url).rstrip("/")
        self._model = model or settings.openrouter_model
        self._site_url = site_url or settings.openrouter_site_url
        self._app_name = app_name or settings.openrouter_app_name

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self._site_url,
            "X-Title": self._app_name,
        }

    async def chat_completion(
        self, messages: list[dict[str, str]], temperature: float = 0.7
    ) -> str:
        """Send a chat completion request and return the assistant's reply text."""
        payload: dict[str, Any] = {
            "model": self._model,
            "messages": messages,
            "temperature": temperature,
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(
                    f"{self._base_url}/chat/completions",
                    headers=self._headers(),
                    json=payload,
                )
            except httpx.HTTPError as exc:
                raise ExternalServiceError(f"Failed to reach OpenRouter: {exc}") from exc

        if response.status_code >= 400:
            raise ExternalServiceError(
                f"OpenRouter returned an error ({response.status_code}): {response.text}"
            )

        data = response.json()
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ExternalServiceError("Unexpected OpenRouter response format") from exc
