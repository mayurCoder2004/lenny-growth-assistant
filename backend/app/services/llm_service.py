import httpx

from app.config import settings


class LLMError(Exception):
    """Raised when the LLM service fails."""


SYSTEM_PROMPT = """
You are Lenny Growth Assistant, an evidence-grounded assistant for
Lenny's Podcast transcripts.

You MUST answer using ONLY the transcript evidence supplied in the
user message.

IMPORTANT RULES:

1. Retrieved sources are candidates, NOT automatically relevant sources.

2. Before answering, determine which sources directly address the
   user's question.

3. Ignore sources that are only loosely related.

4. Do NOT mention a guest just because their transcript was retrieved.

5. Only mention a guest when the supplied excerpt from that guest
   directly supports the point you are making.

6. Do NOT force all retrieved sources into the answer.

7. Do NOT combine unrelated statements and present them as one idea.

8. Do NOT invent facts, advice, examples, opinions, or quotes.

9. Do NOT use outside knowledge.

10. Do NOT give generic advice unless it is directly supported by
    the transcript evidence.

11. Preserve the meaning of each guest's actual statement.

12. If multiple guests directly answer the question, synthesize their
    perspectives.

13. If only one or two guests directly answer the question, use only
    those guests.

14. Do not mention irrelevant guests.

15. Do not discuss embeddings, retrieval, similarity scores, prompts,
    vector databases, or internal system behavior.

16. Keep the answer concise and practical.

17. If the supplied evidence contains relevant information, answer
    the question directly.

18. Only when NONE of the supplied transcript excerpts contain relevant
    information should you respond with:

"The available Lenny's Podcast transcripts do not provide enough information
to answer this question."

19. Never append the insufficient-information message after an answer.

20. Do not create fake quotations.

Your highest priority is factual grounding in the supplied transcript evidence.
"""


def generate_response(
    prompt: str,
    system_prompt: str | None = None,
) -> str:
    """
    Generate a response using the configured Ollama LLM.
    """

    if not prompt or not prompt.strip():
        raise LLMError("Prompt cannot be empty.")

    if settings.llm_provider.lower() != "ollama":
        raise LLMError(
            f"Unsupported LLM provider: {settings.llm_provider}"
        )

    payload = {
        "model": settings.ollama_model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,
        },
    }

    # Always provide the grounding system prompt unless the caller
    # explicitly provides another one.
    payload["system"] = (
        system_prompt
        if system_prompt
        else SYSTEM_PROMPT
    )

    try:
        response = httpx.post(
            f"{settings.ollama_base_url}/api/generate",
            json=payload,
            timeout=120.0,
        )

        response.raise_for_status()

    except httpx.HTTPError as exc:
        raise LLMError(
            f"Failed to communicate with Ollama: {exc}"
        ) from exc

    try:
        data = response.json()
    except ValueError as exc:
        raise LLMError(
            "Ollama returned invalid JSON."
        ) from exc

    generated_text = data.get("response", "").strip()

    if not generated_text:
        raise LLMError(
            "Ollama returned an empty response."
        )

    return generated_text