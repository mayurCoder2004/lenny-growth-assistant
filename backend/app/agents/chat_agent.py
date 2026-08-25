from __future__ import annotations

import asyncio
from typing import Any

from sqlalchemy.orm import Session

from app.agents.base import Agent
from app.claude.runtime import run_grounded_agent


class ChatAgent(Agent):
    """
    Claude-powered grounded chat agent.

    Retrieval and evidence selection remain inside the existing
    grounded RAG pipeline. Claude only receives selected evidence.
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
            raise ValueError("Message cannot be empty.")

        if db is None:
            raise ValueError("A database session is required.")

        try:
            return asyncio.run(
                run_grounded_agent(
                    agent_name=self.name,
                    question=question,
                    db=db,
                    top_k=5,
                    distance_threshold=0.60,
                )
            )
        except RuntimeError as exc:
            if "asyncio.run()" in str(exc):
                raise RuntimeError(
                    "Claude chat execution cannot start a nested event loop."
                ) from exc
            raise
