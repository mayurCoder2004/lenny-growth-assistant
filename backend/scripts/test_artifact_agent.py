from unittest.mock import Mock

from app.agents.artifact_agent import (
    ArtifactAgent,
    ArtifactAgentError,
)

from app.agents.dispatcher import (
    AgentDispatcher,
    AgentDispatcherError,
)

from app.agents.router import (
    AgentRouter,
    AgentRouterError,
)

def test_router_resolves_artifact():
    agent = Mock()

    router = AgentRouter(
        chat_agent=Mock(),
        ship30_agent=Mock(),
        artifact_agent=agent,
    )

    result = router.resolve("artifact")

    assert result is agent

    print("ROUTER ARTIFACT: PASSED")


def test_router_artifact_case_insensitive():
    agent = Mock()

    router = AgentRouter(
        chat_agent=Mock(),
        ship30_agent=Mock(),
        artifact_agent=agent,
    )

    assert router.resolve("ARTIFACT") is agent
    assert router.resolve("Artifact") is agent

    print("ROUTER ARTIFACT CASE INSENSITIVE: PASSED")


def test_dispatcher_calls_artifact_agent():
    agent = Mock()

    agent.execute.return_value = {
        "agent": "artifact",
        "answer": "Artifact routing available.",
        "plan": None,
        "sources": [],
    }

    router = AgentRouter(
        chat_agent=Mock(),
        ship30_agent=Mock(),
        artifact_agent=agent,
    )

    dispatcher = AgentDispatcher(
        router=router,
    )

    db = object()

    result = dispatcher.dispatch(
        db=db,
        agent_name="artifact",
        message="Create a product strategy artifact.",
    )

    assert result["agent"] == "artifact"
    assert result["answer"] == "Artifact routing available."

    agent.execute.assert_called_once_with(
        db=db,
        message="Create a product strategy artifact.",
    )

    print("DISPATCHER ARTIFACT EXECUTION: PASSED")


def test_artifact_agent_requires_message():
    from app.agents.artifact_agent import ArtifactAgent

    agent = ArtifactAgent()

    try:
        agent.execute(
            db=object(),
            message="",
        )
    except ArtifactAgentError as exc:
        assert "Message cannot be empty" in str(exc)
        print("ARTIFACT EMPTY MESSAGE: PASSED")
        return

    raise AssertionError(
        "Expected ValueError."
    )


def test_artifact_agent_requires_database():
    from app.agents.artifact_agent import ArtifactAgent

    agent = ArtifactAgent()

    try:
        agent.execute(
            db=None,
            message="Create an artifact.",
        )
    except ArtifactAgentError as exc:
        assert "database session is required" in str(exc)
        print("ARTIFACT DATABASE REQUIREMENT: PASSED")
        return

    raise AssertionError(
        "Expected ValueError."
    )


if __name__ == "__main__":
    print("=" * 70)
    print("PHASE 7 ARTIFACT AGENT TESTS")
    print("=" * 70)

    test_router_resolves_artifact()
    test_router_artifact_case_insensitive()
    test_dispatcher_calls_artifact_agent()
    test_artifact_agent_requires_message()
    test_artifact_agent_requires_database()

    print()
    print("ALL PHASE 7 ARTIFACT AGENT TESTS PASSED")
