from unittest.mock import patch

from app.services.chat_service import process_chat


class FakeSession:
    pass


PLAN = {
    "goal": "Improve onboarding activation",
}


def test_chat_service_dispatches_ship30():
    db = object()
    session_id = object()

    with patch(
        "app.services.chat_service.get_session",
        return_value=FakeSession(),
    ), patch(
        "app.services.chat_service.add_message",
    ) as add_message_mock, patch(
        "app.services.chat_service.AgentDispatcher",
    ) as dispatcher_class:

        dispatcher = dispatcher_class.return_value

        dispatcher.dispatch.return_value = {
            "agent": "ship30",
            "answer": "Ship30 plan generated.",
            "plan": PLAN,
            "sources": [
                {
                    "evidence_id": "source-1-21",
                }
            ],
        }

        result = process_chat(
            db=db,
            session_id=session_id,
            message="How can I improve onboarding?",
            agent="ship30",
        )

    assert result["answer"] == "Ship30 plan generated."

    assert result["plan"] == PLAN

    assert result["sources"] == [
        {
            "evidence_id": "source-1-21",
        }
    ]

    dispatcher.dispatch.assert_called_once_with(
        db=db,
        agent_name="ship30",
        message="How can I improve onboarding?",
        session_id=session_id,
    )

    assert add_message_mock.call_count == 2

    print("CHAT SERVICE ? SHIP30 DISPATCH: PASSED")


def test_chat_service_defaults_to_chat():
    db = object()
    session_id = object()

    with patch(
        "app.services.chat_service.get_session",
        return_value=FakeSession(),
    ), patch(
        "app.services.chat_service.add_message",
    ) as add_message_mock, patch(
        "app.services.chat_service.AgentDispatcher",
    ) as dispatcher_class:

        dispatcher = dispatcher_class.return_value

        dispatcher.dispatch.return_value = {
            "agent": "chat",
            "answer": "Normal chat answer.",
            "sources": [],
            "plan": None,
        }

        result = process_chat(
            db=db,
            session_id=session_id,
            message="What is product-market fit?",
        )

    assert result["answer"] == "Normal chat answer."

    assert result["plan"] is None

    assert result["sources"] == []

    dispatcher.dispatch.assert_called_once_with(
        db=db,
        agent_name="chat",
        message="What is product-market fit?",
        session_id=session_id,
    )

    assert add_message_mock.call_count == 2

    print("CHAT DEFAULT ? CHAT AGENT DISPATCH: PASSED")


if __name__ == "__main__":
    print("=" * 70)
    print("CHAT SERVICE AGENT INTEGRATION TESTS")
    print("=" * 70)

    test_chat_service_dispatches_ship30()
    test_chat_service_defaults_to_chat()

    print()
    print("ALL CHAT SERVICE AGENT INTEGRATION TESTS PASSED")
