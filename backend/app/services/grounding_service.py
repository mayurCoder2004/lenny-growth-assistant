import re
from typing import Any

from app.schemas.evidence import Evidence
from app.services.evidence_service import candidates_to_evidence


STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by",
    "can", "do", "does", "for", "from", "how", "i",
    "in", "is", "it", "me", "of", "on", "or", "should",
    "that", "the", "their", "this", "to", "was", "what",
    "when", "where", "which", "who", "why", "with",
    "you", "your",
}


def _normalize(text: str) -> str:
    return re.sub(
        r"[^a-z0-9\s]",
        " ",
        text.lower(),
    )


def _tokens(text: str) -> set[str]:
    return {
        token
        for token in _normalize(text).split()
        if (
            token
            and token not in STOP_WORDS
            and len(token) > 2
        )
    }


def _query_phrases(question: str) -> list[str]:
    words = [
        word
        for word in _normalize(question).split()
        if word and word not in STOP_WORDS
    ]

    phrases: list[str] = []

    for size in (2, 3):
        for index in range(len(words) - size + 1):
            phrases.append(
                " ".join(words[index:index + size])
            )

    return phrases


def _lexical_relevance(
    question: str,
    candidate: dict[str, Any],
) -> float:
    query_tokens = _tokens(question)

    if not query_tokens:
        return 0.0

    content = str(candidate.get("content") or "")
    title = str(candidate.get("title") or "")

    content_tokens = _tokens(content)
    title_tokens = _tokens(title)

    token_overlap = (
        len(query_tokens & content_tokens)
        / len(query_tokens)
    )

    title_overlap = (
        len(query_tokens & title_tokens)
        / len(query_tokens)
    )

    normalized_content = _normalize(content)

    phrases = _query_phrases(question)

    phrase_matches = sum(
        1
        for phrase in phrases
        if phrase in normalized_content
    )

    phrase_score = (
        min(phrase_matches, 3) / 3
        if phrases
        else 0.0
    )

    return min(
        token_overlap * 0.55
        + phrase_score * 0.30
        + title_overlap * 0.15,
        1.0,
    )


def _semantic_score(
    candidate: dict[str, Any],
    distance_threshold: float,
) -> float:
    distance = candidate.get("distance")

    if distance is None:
        return 0.0

    try:
        distance_value = float(distance)
    except (TypeError, ValueError):
        return 0.0

    if distance_value < 0:
        return 1.0

    if distance_value >= distance_threshold:
        return 0.0

    return max(
        0.0,
        1.0 - (
            distance_value / distance_threshold
        ),
    )


def _topic_relevance(
    question: str,
    candidate: dict[str, Any],
) -> float:
    """
    Measure whether the candidate discusses the same
    meaningful topic as the question.

    This intentionally uses the candidate title as well
    as transcript content.
    """

    question_tokens = _tokens(question)

    if not question_tokens:
        return 0.0

    content = str(candidate.get("content") or "")
    title = str(candidate.get("title") or "")

    content_tokens = _tokens(content)
    title_tokens = _tokens(title)

    content_overlap = (
        len(question_tokens & content_tokens)
        / len(question_tokens)
    )

    title_overlap = (
        len(question_tokens & title_tokens)
        / len(question_tokens)
    )

    return min(
        content_overlap * 0.75
        + title_overlap * 0.25,
        1.0,
    )


def _combined_relevance(
    semantic: float,
    lexical: float,
    topic: float,
) -> float:
    """
    Semantic similarity helps rank candidates.

    Topic and lexical relevance determine whether
    the candidate is actually useful evidence.
    """

    return (
        semantic * 0.20
        + lexical * 0.35
        + topic * 0.45
    )


def select_grounded_evidence(
    question: str,
    candidates: list[dict[str, Any]],
    max_evidence: int = 5,
    distance_threshold: float = 0.60,
    minimum_relevance: float = 0.15,
    minimum_topic_relevance: float = 0.15,
) -> list[Evidence]:
    """
    Select genuinely relevant evidence from retrieval candidates.

    Retrieval candidates are not automatically evidence.

    Selection uses:

    1. lexical overlap
    2. topic overlap
    3. semantic similarity as a secondary ranking signal

    A candidate must demonstrate actual topic relevance.
    Vector similarity alone is never sufficient.
    """

    if not question or not question.strip():
        return []

    if not candidates:
        return []

    if max_evidence <= 0:
        return []

    scored_candidates: list[
        tuple[float, dict[str, Any]]
    ] = []

    for candidate in candidates:
        semantic = _semantic_score(
            candidate,
            distance_threshold,
        )

        lexical = _lexical_relevance(
            question,
            candidate,
        )

        topic = _topic_relevance(
            question,
            candidate,
        )

        combined = _combined_relevance(
            semantic,
            lexical,
            topic,
        )

        # Grounding requirement:
        # the candidate must actually share meaningful
        # topic overlap with the user's question.
        if topic < minimum_topic_relevance:
            continue

        if combined < minimum_relevance:
            continue

        scored_candidates.append(
            (combined, candidate)
        )

    scored_candidates.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    selected_candidates = [
        candidate
        for _, candidate
        in scored_candidates[:max_evidence]
    ]

    return candidates_to_evidence(
        selected_candidates
    )
