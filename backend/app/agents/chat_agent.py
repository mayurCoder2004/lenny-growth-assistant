from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.agents.base import Agent
from app.services.rag_service import answer_question


class ChatAgent(Agent):
    """
    Agent interface for the existing grounded RAG chat flow.

    The agent remains intentionally thin. Retrieval, grounding,
    context construction, and LLM generation stay inside their
    existing services.
    """

    @property
    def name(self) -> str:
        return "chat"

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

        return answer_question(
            db=db,
            question=question,
            top_k=5,
            distance_threshold=0.70,
        )
