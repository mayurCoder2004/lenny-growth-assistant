from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.agents.base import Agent
from app.services.rag_service import answer_question
from app.services.session_service import get_messages


class ChatAgent(Agent):
    """
    Grounded chat agent with conversation-aware follow-ups.
    """

    @property
    def name(self) -> str:
        return "chat"

    def execute(
        self,
        db: Session | None = None,
        message: str | None = None,
        session_id=None,
        **kwargs: Any,
    ) -> dict:
        question = (
            message
            or kwargs.pop("query", None)
            or ""
        ).strip()

        if not question:
            raise ValueError("Message cannot be empty.")

        if db is None:
            raise ValueError("A database session is required.")

        conversation_context = ""

        if session_id is not None:
            messages = get_messages(
                db=db,
                session_id=session_id,
            )

            previous_messages = messages[:-1][-6:]

            if previous_messages:
                conversation_context = "\n".join(
                    f"{item.role.upper()}: {item.content}"
                    for item in previous_messages
                )

        return answer_question(
            db=db,
            question=question,
            top_k=5,
            distance_threshold=0.60,
            conversation_context=conversation_context,
        )
