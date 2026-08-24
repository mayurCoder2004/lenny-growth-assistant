from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.agents.base import Agent
from app.schemas.ship30 import Ship30Plan
from app.services.ship30_service import (
    Ship30ServiceError,
    generate_ship30,
)


class Ship30AgentError(Exception):
    """Raised when the Ship30 agent fails."""


class Ship30Agent(Agent):
    """
    Agent interface for grounded Ship30 planning.

    The agent is intentionally thin. Retrieval, grounding, generation,
    schema validation, and deterministic plan validation remain inside
    their dedicated services.
    """

    def __init__(
        self,
        candidate_limit: int = 20,
        max_evidence: int = 5,
        distance_threshold: float = 0.60,
    ) -> None:
        self.candidate_limit = candidate_limit
        self.max_evidence = max_evidence
        self.distance_threshold = distance_threshold

    @property
    def name(self) -> str:
        return "ship30"

    def execute(
        self,
        db: Session | None = None,
        session_id: UUID | str | None = None,
        message: str | None = None,
        **kwargs: Any,
    ) -> dict:
        """
        Execute Ship30 planning for a user message.

        Returns the same high-level contract expected from an agent:
            agent
            answer
            plan
            sources
        """

        question = (
            message
            or kwargs.pop("query", None)
            or ""
        ).strip()

        if not question:
            raise Ship30AgentError(
                "Message cannot be empty."
            )

        if db is None:
            raise Ship30AgentError(
                "A database session is required."
            )

        try:
            plan = generate_ship30(
                db=db,
                question=question,
                candidate_limit=self.candidate_limit,
                max_evidence=self.max_evidence,
                distance_threshold=self.distance_threshold,
            )

        except Ship30ServiceError as exc:
            raise Ship30AgentError(
                str(exc)
            ) from exc

        answer = self._render_plan(plan)

        return {
            "agent": self.name,
            "answer": answer,
            "plan": plan,
            "sources": self._extract_sources(plan),
        }

    def run(
        self,
        query: str,
        db: Session,
    ) -> Ship30Plan:
        """
        Generate a Ship30 plan directly.

        Useful for callers that only need the structured plan.
        """

        if not query or not query.strip():
            raise Ship30AgentError(
                "Query cannot be empty."
            )

        if db is None:
            raise Ship30AgentError(
                "A database session is required."
            )

        try:
            return generate_ship30(
                db=db,
                question=query.strip(),
                candidate_limit=self.candidate_limit,
                max_evidence=self.max_evidence,
                distance_threshold=self.distance_threshold,
            )

        except Ship30ServiceError as exc:
            raise Ship30AgentError(
                str(exc)
            ) from exc

    def generate(
        self,
        query: str,
        db: Session,
    ) -> Ship30Plan:
        """Alias for run()."""

        return self.run(
            query=query,
            db=db,
        )

    def _render_plan(
        self,
        plan: Ship30Plan,
    ) -> str:
        """
        Render the structured plan into readable Markdown.

        Evidence IDs remain visible so the answer stays traceable.
        """

        lines: list[str] = [
            "**Goal**",
            "",
            plan.goal,
        ]

        if plan.principles:
            lines.extend(
                [
                    "",
                    "**Principles**",
                    "",
                ]
            )

            for principle in plan.principles:
                lines.append(
                    f"- {principle}"
                )

        phases = [
            ("Days 1-7", plan.days_1_7),
            ("Days 8-14", plan.days_8_14),
            ("Days 15-21", plan.days_15_21),
            ("Days 22-30", plan.days_22_30),
        ]

        for label, phase in phases:
            lines.extend(
                [
                    "",
                    f"**{label}**",
                    "",
                ]
            )

            if not phase.actions:
                lines.append(
                    "- No evidence-supported actions."
                )
                continue

            for action in phase.actions:
                evidence = ", ".join(
                    action.evidence_ids
                )

                lines.append(
                    f"- {action.action} "
                    f"[Evidence: {evidence}]"
                )

        if plan.success:
            lines.extend(
                [
                    "",
                    "**Success Signals**",
                    "",
                ]
            )

            for criterion in plan.success:
                lines.append(
                    f"- {criterion}"
                )

        return "\n".join(lines).strip()

    def _extract_sources(
        self,
        plan: Ship30Plan,
    ) -> list[dict[str, Any]]:
        """
        Return the evidence IDs actually cited by the plan.

        Detailed transcript metadata will be added when the agent layer
        receives the selected Evidence objects directly.
        """

        evidence_ids: list[str] = []

        for phase_name in (
            "days_1_7",
            "days_8_14",
            "days_15_21",
            "days_22_30",
        ):
            phase = getattr(plan, phase_name)

            for action in phase.actions:
                for evidence_id in action.evidence_ids:
                    if evidence_id not in evidence_ids:
                        evidence_ids.append(
                            evidence_id
                        )

        return [
            {
                "evidence_id": evidence_id,
            }
            for evidence_id in evidence_ids
        ]
