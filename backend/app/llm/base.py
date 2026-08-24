from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Base interface for all LLM providers."""

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
    ) -> str:
        """Generate a response from the LLM."""
        raise NotImplementedError