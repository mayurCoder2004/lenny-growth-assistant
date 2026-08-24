import httpx

from app.config import settings
from app.llm.base import LLMProvider


class OllamaProvider(LLMProvider):
    """LLM provider backed by a local Ollama instance."""

    def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
    ) -> str:

        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        payload = {
            "model": settings.ollama_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
            },
        }

        if system_prompt:
            payload["system"] = system_prompt

        try:
            response = httpx.post(
                f"{settings.ollama_base_url}/api/generate",
                json=payload,
                timeout=httpx.Timeout(
                    connect=10.0,
                    read=300.0,
                    write=30.0,
                    pool=10.0,
                ),
            )

            response.raise_for_status()

        except httpx.HTTPError as exc:
            raise RuntimeError(
                f"Failed to communicate with Ollama: {exc}"
            ) from exc

        try:
            data = response.json()
        except ValueError as exc:
            raise RuntimeError(
                "Ollama returned invalid JSON."
            ) from exc

        generated_text = data.get("response", "").strip()

        if not generated_text:
            raise RuntimeError(
                "Ollama returned an empty response."
            )

        return generated_text