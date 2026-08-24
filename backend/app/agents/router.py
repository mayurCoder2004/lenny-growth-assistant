from app.agents.base import Agent
from app.agents.ship30_agent import Ship30Agent


class AgentRouterError(Exception):
    """Raised when an agent cannot be resolved."""


class AgentRouter:
    """
    Resolve the appropriate agent for a request.

    Phase 6 currently exposes Ship30 as the planning agent.
    """

    def __init__(
        self,
        ship30_agent: Agent | None = None,
    ) -> None:
        self.ship30_agent = (
            ship30_agent
            if ship30_agent is not None
            else Ship30Agent()
        )

    def resolve(
        self,
        agent_name: str,
    ) -> Agent:
        name = agent_name.strip().lower()

        if name == "ship30":
            return self.ship30_agent

        raise AgentRouterError(
            f"Unknown agent: {agent_name}"
        )
