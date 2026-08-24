from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.agents.base import Agent


class ArtifactAgent(Agent):
    """
    Agent interface for artifact-oriented requests.

    Phase 7 establishes routing only. The full artifact generation
    pipeline is implemented in the later artifact-generation phase.
    """

    @property
    def name(self) -> str:
        return "artifact"

    def execute(
        self,
        db: Session | None = None,
        message: str | None = None,
        **kwargs: Any,
    ) -> dict:
        question = (
            message
            or kwargs.pop("query", None)
            or ""
        ).strip()

        if not question:
            raise ValueError(
                "Message cannot be empty."
            )

        if db is None:
            raise ValueError(
                "A database session is required."
            )

        return {
            "agent": self.name,
            "answer": (
                "Artifact agent routing is available. "
                "Artifact generation will be implemented "
                "in the artifact generation phase."
            ),
            "plan": None,
            "sources": [],
        }
