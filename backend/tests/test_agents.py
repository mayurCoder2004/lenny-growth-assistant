from unittest.mock import Mock

import pytest

from app.agents.artifact_agent import ArtifactAgent
from app.agents.chat_agent import ChatAgent
from app.agents.dispatcher import AgentDispatcher, AgentDispatcherError
from app.agents.router import AgentRouter
from app.agents.ship30_agent import Ship30Agent


def test_router_resolves_supported_agents():
    router = AgentRouter()

    assert isinstance(router.resolve("chat"), ChatAgent)
    assert isinstance(router.resolve("ship30"), Ship30Agent)
    assert isinstance(router.resolve("artifact"), ArtifactAgent)


def test_dispatcher_returns_controlled_error_for_unknown_agent():
    dispatcher = AgentDispatcher(
        router=AgentRouter(
            chat_agent=Mock(),
            ship30_agent=Mock(),
            artifact_agent=Mock(),
        )
    )

    with pytest.raises(AgentDispatcherError) as exc_info:
        dispatcher.dispatch(
            db=object(),
            agent_name="unknown",
            message="Hello",
        )

    assert "Unknown agent" in str(exc_info.value)
