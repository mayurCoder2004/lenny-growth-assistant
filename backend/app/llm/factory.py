from app.config import settings
from app.llm.base import LLMProvider
from app.llm.ollama_provider import OllamaProvider
from app.llm.anthropic_provider import AnthropicProvider


def get_llm_provider() -> LLMProvider:
    """
    Return the configured LLM provider.
    """

    provider = settings.llm_provider.lower().strip()

    if provider == "ollama":
        return OllamaProvider()

    if provider == "anthropic":
        return AnthropicProvider()

    raise ValueError(
        f"Unsupported LLM provider: {settings.llm_provider}"
    )
