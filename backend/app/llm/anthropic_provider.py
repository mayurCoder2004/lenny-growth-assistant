import httpx

from app.config import settings
from app.llm.base import LLMProvider


class AnthropicProvider(LLMProvider):
    """LLM provider backed by Anthropic Claude."""

    def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
    ) -> str:

        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        if not settings.anthropic_api_key:
            raise RuntimeError(
                "Anthropic API key is not configured."
            )

        if not settings.anthropic_model:
            raise RuntimeError(
                "Anthropic model is not configured."
            )

        payload = {
            "model": settings.anthropic_model,
            "max_tokens": 1024,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        }

        if system_prompt:
            payload["system"] = system_prompt

        headers = {
            "x-api-key": settings.anthropic_api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

        try:
            response = httpx.post(
                "https://api.anthropic.com/v1/messages",
                json=payload,
                headers=headers,
                timeout=httpx.Timeout(
                    connect=10.0,
                    read=120.0,
                    write=30.0,
                    pool=10.0,
                ),
            )

            response.raise_for_status()

        except httpx.HTTPError as exc:
            raise RuntimeError(
                f"Failed to communicate with Anthropic: {exc}"
            ) from exc

        try:
            data = response.json()
        except ValueError as exc:
            raise RuntimeError(
                "Anthropic returned invalid JSON."
            ) from exc

        content = data.get("content", [])

        if not content:
            raise RuntimeError(
                "Anthropic returned an empty response."
            )

        generated_text = "".join(
            block.get("text", "")
            for block in content
            if block.get("type") == "text"
        ).strip()

        if not generated_text:
            raise RuntimeError(
                "Anthropic returned an empty response."
            )

        return generated_text
