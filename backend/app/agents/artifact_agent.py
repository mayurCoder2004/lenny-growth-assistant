from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.agents.base import Agent
from app.services.ship30_skill_service import (
    Ship30SkillService,
    Ship30SkillServiceError,
)


class ArtifactAgentError(Exception):
    """Raised when the artifact agent fails."""


class ArtifactAgent(Agent):
    """
    Agent interface for artifact-oriented requests.

    Phase 8 connects artifact requests to the grounded Ship30
    writing skill.

    Flow:

        Artifact request
            ?
        Ship30SkillService
            ?
        Retrieval
            ?
        Grounding
            ?
        Ship30Skill
            ?
        Ship30Essay
    """

    def __init__(
        self,
        skill_service: Ship30SkillService | None = None,
    ) -> None:
        self.skill_service = (
            skill_service
            if skill_service is not None
            else Ship30SkillService()
        )

    @property
    def name(self) -> str:
        return "artifact"

    def execute(
        self,
        db: Session | None = None,
        session_id: UUID | str | None = None,
        message: str | None = None,
        **kwargs: Any,
    ) -> dict:
        """
        Generate a grounded Ship30-style written artifact.
        """

        question = (
            message
            or kwargs.pop("query", None)
            or ""
        ).strip()

        if not question:
            raise ArtifactAgentError(
                "Message cannot be empty."
            )

        if db is None:
            raise ArtifactAgentError(
                "A database session is required."
            )

        try:
            essay = self.skill_service.generate(
                db=db,
                question=question,
            )

        except Ship30SkillServiceError as exc:
            raise ArtifactAgentError(
                str(exc)
            ) from exc

        except Exception as exc:
            raise ArtifactAgentError(
                f"Failed to generate artifact: {exc}"
            ) from exc

        return {
            "agent": self.name,
            "answer": essay.content,
            "plan": None,
            "sources": [
                {
                    "evidence_id": evidence_id,
                }
                for evidence_id in essay.evidence_ids
            ],
        }
