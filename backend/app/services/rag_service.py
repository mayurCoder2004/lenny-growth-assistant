from sqlalchemy.orm import Session

from app.services.context_service import build_transcript_context
from app.services.grounding_service import select_grounded_evidence
from app.services.llm_service import (
    generate_response,
    rewrite_question,
)
from app.services.retrieval_service import search_similar_chunks
from app.logging_config import logger


INSUFFICIENT_CONTEXT_MESSAGE = (
    "The available Lenny's Podcast transcripts do not provide enough "
    "information to answer this question."
)


DEFAULT_DISTANCE_THRESHOLD = 0.60


SYSTEM_PROMPT = """
You are Lenny Growth Assistant.

Answer the user's question using ONLY the transcript evidence provided.

The evidence has already been selected and grounded by the application.

Rules:

- Use only information present in the transcript evidence.
- Do not use outside knowledge.
- Do not invent facts.
- Do not invent quotes.
- Do not mention retrieval, embeddings, similarity scores,
  prompts, context windows, or internal system behavior.
- Ignore evidence that does not help answer the question.
- Mention a guest by name when presenting their perspective.
- Combine perspectives only when they are directly relevant.
- Do not add generic advice unsupported by the evidence.

Return ONLY the final answer.
"""


def _build_sources(
    evidence,
) -> list[dict]:
    """
    Convert grounded Evidence objects into API-friendly sources.
    """

    return [
        {
            "guest": item.guest,
            "title": item.title,
            "url": item.url,
            "distance": item.distance,
            "chunk_index": item.chunk_index,
        }
        for item in evidence
    ]


def _clean_answer(answer: str) -> str:
    """
    Clean obvious model artifacts without changing substance.
    """

    if not answer:
        return ""

    answer = answer.strip()

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


def _build_grounded_context(
    evidence,
) -> str:
    """
    Build context from grounded Evidence objects.

    Evidence IDs are explicitly included so later structured
    generation can reference them.
    """

    if not evidence:
        return ""

    context_parts: list[str] = []

    for item in evidence:
        context_parts.append(
            f"""
EVIDENCE ID: {item.evidence_id}

Guest: {item.guest}
Episode: {item.title}

Transcript excerpt:
{item.content}
""".strip()
        )

    return "\n\n".join(context_parts)



def retrieve_grounded_context(
    db: Session,
    question: str,
    top_k: int = 5,
    distance_threshold: float = DEFAULT_DISTANCE_THRESHOLD,
) -> dict:
    """
    Retrieve and ground transcript evidence without generating an answer.

    This separates evidence retrieval from answer generation so that
    different agent runtimes can consume the same grounded context.
    """

    if not question or not question.strip():
        return {
            "question": "",
            "context": "",
            "evidence": [],
        }

    question = question.strip()

    candidate_limit = max(top_k * 4, 20)

    candidates = search_similar_chunks(
        db=db,
        query=retrieval_question,
        limit=candidate_limit,
        candidate_limit=candidate_limit,
    )

    if not candidates:
        return {
            "question": question,
            "context": "",
            "evidence": [],
        }

    evidence = select_grounded_evidence(
        question=question,
        candidates=candidates,
        max_evidence=top_k,
        distance_threshold=distance_threshold,
    )

    if not evidence:
        return {
            "question": question,
            "context": "",
            "evidence": [],
        }

    context = _build_grounded_context(evidence)

    if not context.strip():
        return {
            "question": question,
            "context": "",
            "evidence": [],
        }

    return {
        "question": question,
        "context": context,
        "evidence": evidence,
    }

def answer_question(
    db: Session,
    question: str,
    top_k: int = 5,
    distance_threshold: float = DEFAULT_DISTANCE_THRESHOLD,
    conversation_context: str = "",
) -> dict:
    """
    Grounded RAG pipeline:

        Question
            ?
        Retrieval
            ?
        Grounding / relevance filtering
            ?
        Selected Evidence
            ?
        Grounded context
            ?
        LLM generation
            ?
        Answer + grounded sources
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

    # Rewrite follow-up questions into standalone retrieval queries.
    retrieval_question = rewrite_question(
        question=question,
        conversation_context=conversation_context,
    )

    # ============================================================
    # 2. Retrieve candidate evidence
    # ============================================================

    candidate_limit = max(top_k * 4, 20)

    candidates = search_similar_chunks(
        db=db,
        query=retrieval_question,
        limit=candidate_limit,
        candidate_limit=candidate_limit,
    )

    print("\n" + "=" * 80)
    print("RETRIEVAL CANDIDATES")
    print("=" * 80)

    if not candidates:
        print("No retrieval candidates.")

        return {
            "answer": INSUFFICIENT_CONTEXT_MESSAGE,
            "sources": [],
        }

    for index, candidate in enumerate(
        candidates,
        start=1,
    ):
        print(
            f"{index}. "
            f"{candidate.get('guest')} | "
            f"distance={candidate.get('distance')} | "
            f"chunk={candidate.get('chunk_index')}"
        )

    # ============================================================
    # 3. Ground candidates
    # ============================================================

    evidence = select_grounded_evidence(
        question=question,
        candidates=candidates,
        max_evidence=top_k,
        distance_threshold=distance_threshold,
    )

    print("\n" + "=" * 80)
    print("GROUNDED EVIDENCE")
    print("=" * 80)

    if not evidence:
        print("No sufficiently relevant evidence selected.")

        return {
            "answer": INSUFFICIENT_CONTEXT_MESSAGE,
            "sources": [],
        }

    for index, item in enumerate(
        evidence,
        start=1,
    ):
        print(
            f"{index}. "
            f"{item.evidence_id} | "
            f"{item.guest} | "
            f"{item.title} | "
            f"distance={item.distance}"
        )

    # ============================================================
    # 4. Build grounded context
    # ============================================================

    context = _build_grounded_context(evidence)

    if not context.strip():
        return {
            "answer": INSUFFICIENT_CONTEXT_MESSAGE,
            "sources": [],
        }

    print("\n" + "=" * 80)
    print("GROUNDED CONTEXT SENT TO LLM")
    print("=" * 80)

    print(context)

    # ============================================================
    # 5. Build grounded prompt
    # ============================================================

    prompt = f"""
CONVERSATION CONTEXT:

{conversation_context or "No previous conversation context."}


CURRENT USER QUESTION:

{question}


SELECTED TRANSCRIPT EVIDENCE:

{context}


TASK:

Answer the user's question using ONLY the selected transcript evidence.

Use only evidence that directly helps answer the question.

Mention guests by name when presenting their perspectives.

If multiple pieces of evidence directly answer the question,
synthesize them into one clear answer.

Do not invent facts.

Do not use outside knowledge.

Do not invent quotes.

Do not add generic advice that is not supported by the evidence.

Return ONLY the final answer.
""".strip()

    # ============================================================
    # 6. Generate answer
    # ============================================================

    logger.info("RAG answer generation started | evidence=%d", len(evidence))

    answer = generate_response(
        prompt=prompt,
        system_prompt=SYSTEM_PROMPT,
    )

    answer = _clean_answer(answer)

    if not answer:
        answer = INSUFFICIENT_CONTEXT_MESSAGE

    # ============================================================
    # 7. Return grounded response
    # ============================================================

    sources = _build_sources(evidence)

    logger.info("RAG request completed | evidence=%d | sources=%d", len(evidence), len(sources))

    print("\n" + "=" * 80)
    print("FINAL ANSWER")
    print("=" * 80)

    print(answer)

    return {
        "answer": answer,
        "sources": sources,
    }

