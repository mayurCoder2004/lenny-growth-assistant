from sqlalchemy.orm import Session

from app.services.grounding_service import select_grounded_evidence
from app.services.retrieval_service import search_similar_chunks
from app.services.ship30_generation_service import (
    generate_ship30_plan,
)


class Ship30ServiceError(Exception):
    """Raised when the Ship30 service fails."""


DEFAULT_DISTANCE_THRESHOLD = 0.60
DEFAULT_CANDIDATE_LIMIT = 20
DEFAULT_MAX_EVIDENCE = 5


def generate_ship30(
    db: Session,
    question: str,
    candidate_limit: int = DEFAULT_CANDIDATE_LIMIT,
    max_evidence: int = DEFAULT_MAX_EVIDENCE,
    distance_threshold: float = DEFAULT_DISTANCE_THRESHOLD,
):
    """
    Generate a grounded 30-day Ship30 plan.

    Flow:

        User goal
            ?
        Semantic retrieval
            ?
        Evidence grounding
            ?
        Structured Ship30 generation
            ?
        Plan validation
            ?
        Validated Ship30Plan
    """

    if not question or not question.strip():
        raise Ship30ServiceError(
            "Question cannot be empty."
        )

    question = question.strip()

    if candidate_limit <= 0:
        raise Ship30ServiceError(
            "candidate_limit must be greater than zero."
        )

    if max_evidence <= 0:
        raise Ship30ServiceError(
            "max_evidence must be greater than zero."
        )

    candidates = search_similar_chunks(
        db=db,
        query=question,
        limit=candidate_limit,
        candidate_limit=candidate_limit,
    )

    if not candidates:
        raise Ship30ServiceError(
            "No retrieval candidates were found."
        )

    evidence = select_grounded_evidence(
        question=question,
        candidates=candidates,
        max_evidence=max_evidence,
        distance_threshold=distance_threshold,
    )

    if not evidence:
        raise Ship30ServiceError(
            "No sufficiently relevant evidence was found."
        )

    try:
        plan = generate_ship30_plan(
            question=question,
            evidence=evidence,
        )
    except Exception as exc:
        raise Ship30ServiceError(
            f"Failed to generate Ship30 plan: {exc}"
        ) from exc

    return plan
