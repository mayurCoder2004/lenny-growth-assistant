import pytest

from app.services.llm_service import LLMError, generate_response


class FailingProvider:
    def generate(self, prompt, system_prompt=None):
        raise RuntimeError("Ollama unavailable")


class EmptyProvider:
    def generate(self, prompt, system_prompt=None):
        return ""


def test_llm_provider_failures_and_empty_responses_are_controlled(
    monkeypatch,
):
    monkeypatch.setattr(
        "app.services.llm_service.get_llm_provider",
        lambda: FailingProvider(),
    )

    with pytest.raises(LLMError) as failure:
        generate_response("Answer from evidence.")

    assert "Failed to generate response" in str(failure.value)
    assert "Ollama unavailable" in str(failure.value)

    monkeypatch.setattr(
        "app.services.llm_service.get_llm_provider",
        lambda: EmptyProvider(),
    )

    with pytest.raises(LLMError) as empty:
        generate_response("Answer from evidence.")

    assert "empty response" in str(empty.value)
