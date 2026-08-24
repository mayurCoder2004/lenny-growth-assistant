from typing import Any

from sqlalchemy.orm import Session

from app.agents.router import (
    AgentRouter,
    AgentRouterError,
)


class AgentDispatcherError(Exception):
    """Raised when agent dispatch fails."""


class AgentDispatcher:
    """
    Dispatch requests to the appropriate application agent.
    """

    def __init__(
        self,
        router: AgentRouter | None = None,
    ) -> None:
        self.router = (
            router
            if router is not None
            else AgentRouter()
        )

    def dispatch(
        self,
        db: Session,
        agent_name: str,
        **kwargs: Any,
    ) -> dict:
        if not agent_name or not agent_name.strip():
            raise AgentDispatcherError(
                "Agent name cannot be empty."
            )

        try:
            agent = self.router.resolve(
                agent_name
            )

            return agent.execute(
                db=db,
                **kwargs,
            )

        except AgentRouterError as exc:
            raise AgentDispatcherError(
                str(exc)
            ) from exc
        except Exception as exc:
            raise AgentDispatcherError(
                f"Agent execution failed: {exc}"
            ) from exc
