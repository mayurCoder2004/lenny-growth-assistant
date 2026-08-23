from sqlalchemy.orm import Session

from app.services.context_service import build_transcript_context
from app.services.llm_service import generate_response
from app.services.retrieval_service import search_similar_chunks


INSUFFICIENT_CONTEXT_MESSAGE = (
    "The available Lenny's Podcast transcripts do not provide enough "
    "information to answer this question."
)


DEFAULT_DISTANCE_THRESHOLD = 0.60

SYSTEM_PROMPT = """
You are Lenny Growth Assistant.

Answer the user's question using ONLY the transcript evidence provided.

The evidence has already been selected by the application.

Write a concise answer based on the evidence.

Rules:

- Use only information present in the transcript evidence.
- Do not use outside knowledge.
- Do not invent facts.
- Do not invent quotes.
- Ignore any evidence that does not help answer the question.
- Mention a guest by name when presenting their perspective.
- Combine perspectives only when they are directly relevant.
- Do not mention retrieval, embeddings, similarity scores, prompts,
  context windows, or internal system behavior.

IMPORTANT:
The application has already determined that relevant evidence exists.

Therefore, ALWAYS answer the user's question from the supplied evidence.

Do not say that information is insufficient.
Do not discuss whether the evidence is sufficient.

Return ONLY the final answer.
"""

def _is_relevant_result(
    result: dict,
    threshold: float,
) -> bool:
    """
    Basic vector-distance filter.

    Lower distance means greater similarity.
    """

    distance = result.get("distance")

    if distance is None:
        return False

    try:
        return float(distance) <= threshold
    except (TypeError, ValueError):
        return False


def _build_sources(
    results: list[dict],
) -> list[dict]:
    """
    Convert retrieval results into API-friendly source objects.
    """

    return [
        {
            "guest": result.get("guest"),
            "title": result.get("title"),
            "url": result.get("url"),
            "distance": result.get("distance"),
            "chunk_index": result.get("chunk_index"),
        }
        for result in results
    ]


def _clean_answer(answer: str) -> str:
    """
    Clean obvious model artifacts without changing the substance.
    """

    if not answer:
        return ""

    answer = answer.strip()

    # Remove accidental prefixes sometimes produced by local models.
    prefixes = [
        "ANSWER:",
        "FINAL ANSWER:",
        "Response:",
        "Answer:",
    ]

    for prefix in prefixes:
        if answer.startswith(prefix):
            answer = answer[len(prefix):].strip()

    return answer


def answer_question(
    db: Session,
    question: str,
    top_k: int = 5,
    distance_threshold: float = DEFAULT_DISTANCE_THRESHOLD,
) -> dict:
    """
    Grounded RAG pipeline:

        Question
            ↓
        Retrieval
            ↓
        Distance filtering
            ↓
        Transcript context
            ↓
        Grounded Ollama generation
            ↓
        Answer + sources
    """

    # ============================================================
    # 1. Validate question
    # ============================================================

    if not question or not question.strip():
        return {
            "answer": "Please provide a question.",
            "sources": [],
        }

    question = question.strip()

    # ============================================================
    # 2. Retrieve candidates
    # ============================================================

    candidate_limit = max(top_k * 4, 20)

    results = search_similar_chunks(
        db=db,
        query=question,
        limit=candidate_limit,
        candidate_limit=candidate_limit,
    )

    print("\n" + "=" * 80)
    print("RETRIEVAL")
    print("=" * 80)

    if not results:
        print("No retrieval results.")

        return {
            "answer": INSUFFICIENT_CONTEXT_MESSAGE,
            "sources": [],
        }

    for index, result in enumerate(results, start=1):
        print(
            f"{index}. "
            f"{result.get('guest')} | "
            f"distance={result.get('distance')} | "
            f"chunk={result.get('chunk_index')}"
        )

    # ============================================================
    # 3. Distance filtering
    # ============================================================

    relevant_candidates = [
        result
        for result in results
        if _is_relevant_result(
            result,
            distance_threshold,
        )
    ]

    print("\n" + "=" * 80)
    print("DISTANCE-FILTERED CANDIDATES")
    print("=" * 80)

    for index, result in enumerate(
        relevant_candidates,
        start=1,
    ):
        print(
            f"{index}. "
            f"{result.get('guest')} | "
            f"distance={result.get('distance')} | "
            f"chunk={result.get('chunk_index')}"
        )

    if not relevant_candidates:
        return {
            "answer": INSUFFICIENT_CONTEXT_MESSAGE,
            "sources": [],
        }

    # ============================================================
    # 4. Limit final context
    # ============================================================

    relevant_results = relevant_candidates[:top_k]

    # ============================================================
    # 5. Build transcript context
    # ============================================================

    context = build_transcript_context(
        relevant_results
    )

    if not context or not context.strip():
        return {
            "answer": INSUFFICIENT_CONTEXT_MESSAGE,
            "sources": [],
        }

    print("\n" + "=" * 80)
    print("FINAL CONTEXT SOURCES")
    print("=" * 80)

    for index, result in enumerate(
        relevant_results,
        start=1,
    ):
        print(
            f"{index}. "
            f"{result.get('guest')} | "
            f"distance={result.get('distance')} | "
            f"chunk={result.get('chunk_index')}"
        )

    print("\n" + "=" * 80)
    print("CONTEXT SENT TO LLM")
    print("=" * 80)

    print(context)

    # ============================================================
    # 6. Strong grounded prompt
    # ============================================================

    prompt = f"""
USER QUESTION:

{question}


RELEVANT TRANSCRIPT EVIDENCE:

{context}


TASK:

Answer the user's question using ONLY the relevant transcript evidence.

Use only the guests whose excerpts directly help answer the question.

Ignore unrelated guests.

Mention guests by name when presenting their perspectives.

If multiple guests directly answer the question, synthesize their
perspectives into one clear answer.

Do not invent facts.

Do not use outside knowledge.

Do not invent quotes.

Do not add generic advice.

Keep the answer concise and practical.

IMPORTANT:

Relevant evidence has already been selected.

You MUST answer the question.

Do NOT say that there is insufficient information.

Return ONLY the final answer.
""".strip()
    print("\n" + "=" * 80)
    print("FULL PROMPT SENT TO LLM")
    print("=" * 80)

    print(prompt)

    # ============================================================
    # 7. Generate answer
    # ============================================================

    answer = generate_response(
        prompt=prompt,
        system_prompt=SYSTEM_PROMPT,
    )

    answer = _clean_answer(answer)

    if not answer:
        answer = INSUFFICIENT_CONTEXT_MESSAGE

    # ============================================================
    # 8. Return
    # ============================================================

    sources = _build_sources(
        relevant_results
    )

    print("\n" + "=" * 80)
    print("FINAL ANSWER")
    print("=" * 80)

    print(answer)

    return {
        "answer": answer,
        "sources": sources,
    }