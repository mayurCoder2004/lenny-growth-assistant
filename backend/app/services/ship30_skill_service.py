from sqlalchemy.orm import Session

from app.schemas.evidence import Evidence
from app.services.grounding_service import select_grounded_evidence
from app.services.retrieval_service import search_similar_chunks
from app.skills.ship30_skill import (
    Ship30Essay,
    Ship30Skill,
    Ship30SkillError,
)


class Ship30SkillServiceError(Exception):
    """Raised when Ship30 skill orchestration fails."""


DEFAULT_CANDIDATE_LIMIT = 20
DEFAULT_MAX_EVIDENCE = 5
DEFAULT_DISTANCE_THRESHOLD = 0.60


class Ship30SkillService:
    """
    Orchestrate retrieval, grounding, and Ship30 essay generation.

    Retrieval and grounding remain separate from the writing skill.

    Flow:

        Question
            ?
        Semantic retrieval
            ?
        Evidence grounding
            ?
        Ship30Skill
            ?
        Ship30Essay
    """

    def __init__(
        self,
        skill: Ship30Skill | None = None,
        candidate_limit: int = DEFAULT_CANDIDATE_LIMIT,
        max_evidence: int = DEFAULT_MAX_EVIDENCE,
        distance_threshold: float = DEFAULT_DISTANCE_THRESHOLD,
    ) -> None:
        self.skill = (
            skill
            if skill is not None
            else Ship30Skill()
        )

        self.candidate_limit = candidate_limit
        self.max_evidence = max_evidence
        self.distance_threshold = distance_threshold

    def generate(
        self,
        db: Session,
        question: str,
    ) -> Ship30Essay:
        """
        Generate a grounded Ship30 essay.

        The service is responsible for orchestration only.
        """

        if not question or not question.strip():
            raise Ship30SkillServiceError(
                "Question cannot be empty."
            )

        if db is None:
            raise Ship30SkillServiceError(
                "A database session is required."
            )

        if self.candidate_limit <= 0:
            raise Ship30SkillServiceError(
                "candidate_limit must be greater than zero."
            )

        if self.max_evidence <= 0:
            raise Ship30SkillServiceError(
                "max_evidence must be greater than zero."
            )

        question = question.strip()

        candidates = search_similar_chunks(
            db=db,
            query=question,
            limit=self.candidate_limit,
            candidate_limit=self.candidate_limit,
        )

        if not candidates:
            raise Ship30SkillServiceError(
                "No retrieval candidates were found."
            )

        evidence = select_grounded_evidence(
            question=question,
            candidates=candidates,
            max_evidence=self.max_evidence,
            distance_threshold=self.distance_threshold,
        )

        if not evidence:
            raise Ship30SkillServiceError(
                "No sufficiently relevant evidence was found."
            )

        try:
            return self.skill.generate(
                question=question,
                evidence=evidence,
            )

        except Ship30SkillError as exc:
            raise Ship30SkillServiceError(
                str(exc)
            ) from exc

        except Exception as exc:
            raise Ship30SkillServiceError(
                f"Failed to generate Ship30 essay: {exc}"
            ) from exc
