from app.llm.factory import get_llm_provider


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
    Generate a response using the configured LLM provider.
    """

    if not prompt or not prompt.strip():
        raise LLMError("Prompt cannot be empty.")

    provider = get_llm_provider()

    try:
        response = provider.generate(
            prompt=prompt,
            system_prompt=(
                system_prompt
                if system_prompt
                else SYSTEM_PROMPT
            ),
        )

    except Exception as exc:
        raise LLMError(
            f"Failed to generate response: {exc}"
        ) from exc

    if not response or not response.strip():
        raise LLMError(
            "LLM returned an empty response."
        )

    return response.strip()


def rewrite_question(
    question: str,
    conversation_context: str = "",
) -> str:
    """
    Rewrite a follow-up question into a standalone question
    suitable for transcript retrieval.
    """

    question = (question or "").strip()

    if not question:
        raise LLMError("Question cannot be empty.")

    if not conversation_context.strip():
        return question

    prompt = f"""
CONVERSATION:

{conversation_context}


CURRENT QUESTION:

{question}


TASK:

Rewrite the CURRENT QUESTION as a standalone search question.

Use the conversation only to resolve references such as:
- "that"
- "this"
- "it"
- "they"
- "the above"
- "explain more"
- "why?"
- "how?"
- "what about?"

Preserve the user's actual intent.

Do not answer the question.

Do not add new information.

Return ONLY the rewritten standalone question.
""".strip()

    try:
        rewritten = generate_response(
            prompt=prompt,
            system_prompt=(
                "You rewrite follow-up questions into standalone "
                "questions for transcript retrieval. "
                "Return only the rewritten question."
            ),
        )

    except Exception as exc:
        raise LLMError(
            f"Failed to rewrite question: {exc}"
        ) from exc

    rewritten = rewritten.strip()

    if not rewritten:
        return question

    return rewritten
