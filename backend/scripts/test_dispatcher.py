from unittest.mock import Mock

from app.agents.dispatcher import (
    AgentDispatcher,
    AgentDispatcherError,
)
from app.agents.router import (
    AgentRouter,
    AgentRouterError,
)


def test_router_resolves_chat():
    agent = Mock()
    router = AgentRouter(
        chat_agent=agent,
        ship30_agent=Mock(),
    )

    result = router.resolve("chat")

    assert result is agent

    print("ROUTER CHAT: PASSED")


def test_router_resolves_ship30():
    agent = Mock()
    router = AgentRouter(
        ship30_agent=agent,
    )

    result = router.resolve("ship30")

    assert result is agent

    print("ROUTER SHIP30: PASSED")


def test_router_is_case_insensitive():
    agent = Mock()
    router = AgentRouter(
        chat_agent=agent,
        ship30_agent=Mock(),
    )

    assert router.resolve("CHAT") is agent
    assert router.resolve("Chat") is agent

    ship30_agent = router.resolve("SHIP30")
    assert ship30_agent is router.ship30_agent

    print("ROUTER CASE INSENSITIVE: PASSED")


def test_router_rejects_unknown_agent():
    router = AgentRouter(
        chat_agent=Mock(),
        ship30_agent=Mock(),
    )

    try:
        router.resolve("unknown")
    except AgentRouterError as exc:
        assert "Unknown agent" in str(exc)
        print("ROUTER UNKNOWN AGENT: PASSED")
        return

    raise AssertionError(
        "Expected AgentRouterError."
    )


def test_dispatcher_calls_resolved_agent():
    agent = Mock()

    agent.execute.return_value = {
        "agent": "ship30",
        "answer": "test answer",
        "plan": None,
        "sources": [],
    }

    router = AgentRouter(
        ship30_agent=agent,
    )

    dispatcher = AgentDispatcher(
        router=router,
    )

    db = object()

    result = dispatcher.dispatch(
        db=db,
        agent_name="ship30",
        message="How can I improve onboarding?",
    )

    assert result["agent"] == "ship30"
    assert result["answer"] == "test answer"

    agent.execute.assert_called_once_with(
        db=db,
        message="How can I improve onboarding?",
    )

    print("DISPATCHER SHIP30 EXECUTION: PASSED")


def test_dispatcher_calls_chat_agent():
    agent = Mock()

    agent.execute.return_value = {
        "agent": "chat",
        "answer": "chat answer",
        "sources": [],
    }

    router = AgentRouter(
        chat_agent=agent,
        ship30_agent=Mock(),
    )

    dispatcher = AgentDispatcher(
        router=router,
    )

    db = object()

    result = dispatcher.dispatch(
        db=db,
        agent_name="chat",
        message="What is product-market fit?",
    )

    assert result["agent"] == "chat"
    assert result["answer"] == "chat answer"

    agent.execute.assert_called_once_with(
        db=db,
        message="What is product-market fit?",
    )

    print("DISPATCHER CHAT EXECUTION: PASSED")


def test_dispatcher_rejects_empty_agent():
    dispatcher = AgentDispatcher()

    try:
        dispatcher.dispatch(
            db=object(),
            agent_name="",
            message="test",
        )
    except AgentDispatcherError as exc:
        assert "Agent name cannot be empty" in str(exc)
        print("DISPATCHER EMPTY AGENT: PASSED")
        return

    raise AssertionError(
        "Expected AgentDispatcherError."
    )


def test_dispatcher_wraps_router_error():
    dispatcher = AgentDispatcher()

    try:
        dispatcher.dispatch(
            db=object(),
            agent_name="unknown",
            message="test",
        )
    except AgentDispatcherError as exc:
        assert "Unknown agent" in str(exc)
        print("DISPATCHER UNKNOWN AGENT: PASSED")
        return

    raise AssertionError(
        "Expected AgentDispatcherError."
    )


if __name__ == "__main__":
    print("=" * 70)
    print("AGENT ROUTER + DISPATCHER TESTS")
    print("=" * 70)

    test_router_resolves_chat()
    test_router_resolves_ship30()
    test_router_is_case_insensitive()
    test_router_rejects_unknown_agent()
    test_dispatcher_calls_resolved_agent()
    test_dispatcher_calls_chat_agent()
    test_dispatcher_rejects_empty_agent()
    test_dispatcher_wraps_router_error()

    print()
    print("ALL ROUTER + DISPATCHER TESTS PASSED")
