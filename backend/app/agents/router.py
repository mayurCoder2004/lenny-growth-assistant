from app.agents.base import Agent
from app.agents.artifact_agent import ArtifactAgent
from app.agents.chat_agent import ChatAgent
from app.agents.ship30_agent import Ship30Agent


class AgentRouterError(Exception):
    """Raised when an agent cannot be resolved."""


class AgentRouter:
    """
    Resolve the appropriate agent for a request.

    Supported agents:
        chat     -> ChatAgent
        ship30   -> Ship30Agent
        artifact -> ArtifactAgent
    """

    def __init__(
        self,
        chat_agent: Agent | None = None,
        ship30_agent: Agent | None = None,
        artifact_agent: Agent | None = None,
    ) -> None:
        self.chat_agent = (
            chat_agent
            if chat_agent is not None
            else ChatAgent()
        )

        self.ship30_agent = (
            ship30_agent
            if ship30_agent is not None
            else Ship30Agent()
        )

        self.artifact_agent = (
            artifact_agent
            if artifact_agent is not None
            else ArtifactAgent()
        )

    def resolve(
        self,
        agent_name: str,
    ) -> Agent:
        if not agent_name or not agent_name.strip():
            raise AgentRouterError(
                "Agent name cannot be empty."
            )

        name = agent_name.strip().lower()

        if name == "chat":
            return self.chat_agent

        if name == "ship30":
            return self.ship30_agent

        if name == "artifact":
            return self.artifact_agent

        raise AgentRouterError(
            f"Unknown agent: {agent_name}"
        )
