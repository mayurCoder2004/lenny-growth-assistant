from unittest.mock import patch
from uuid import uuid4

from app.models import Artifact, Message
from app.services.chat_service import process_chat


class FakeSession:
    def __init__(
        self,
        session_id,
        title="New Chat",
    ):
        self.id = session_id
        self.title = title


class FakeMessage:
    def __init__(self, session_id, role, content):
        self.id = uuid4()
        self.session_id = session_id
        self.role = role
        self.content = content


class FakeScalarResult:
    def all(self):
        return []


class FakeDB:
    def __init__(self):
        self.messages = []
        self.artifacts = []

    def add(self, value):
        if isinstance(value, Message):
            self.messages.append(value)

        if isinstance(value, Artifact):
            self.artifacts.append(value)

    def commit(self):
        pass

    def refresh(self, value):
        pass

    def get(self, model, object_id):
        if model.__name__ == "Session":
            return None

        if model is Artifact:
            for artifact in self.artifacts:
                if artifact.id == object_id:
                    return artifact

        return None

    def scalars(self, statement):
        return FakeScalarResult()


def test_artifact_chat_persistence():
    db = FakeDB()
    session_id = uuid4()

    assistant_message = FakeMessage(
        session_id=session_id,
        role="assistant",
        content="A grounded Ship30 essay.",
    )

    def fake_add_message(db, session_id, role, content):
        if role == "user":
            return FakeMessage(
                session_id=session_id,
                role=role,
                content=content,
            )

        return assistant_message

    class FakeDispatcher:
        def dispatch(self, db, agent_name, **kwargs):
            assert agent_name == "artifact"

            return {
                "answer": "A grounded Ship30 essay.",
                "sources": [
                    {
                        "evidence_id": "evidence-1",
                    }
                ],
                "plan": None,
            }

    with patch(
        "app.services.chat_service.get_session",
        return_value=FakeSession(session_id),
    ), patch(
        "app.services.chat_service.add_message",
        side_effect=fake_add_message,
    ), patch(
        "app.services.chat_service.AgentDispatcher",
        return_value=FakeDispatcher(),
    ) as dispatcher_cls, patch(
        "app.services.chat_service.create_artifact",
    ) as create_artifact_mock:

        result = process_chat(
            db=db,
            session_id=session_id,
            message="Write an essay about product retention.",
            agent="artifact",
        )

    dispatcher_cls.assert_called_once()

    create_artifact_mock.assert_called_once_with(
        db=db,
        session_id=session_id,
        message_id=assistant_message.id,
        artifact_type="essay",
        title="Ship30 Essay",
        content="A grounded Ship30 essay.",
    )

    assert result["answer"] == "A grounded Ship30 essay."

    print("ARTIFACT CHAT DISPATCH: PASSED")
    print("ASSISTANT MESSAGE CAPTURE: PASSED")
    print("ARTIFACT MESSAGE LINK: PASSED")
    print("ARTIFACT CONTENT PERSISTENCE: PASSED")


def test_non_artifact_chat_does_not_create_artifact():
    db = FakeDB()
    session_id = uuid4()

    class FakeDispatcher:
        def dispatch(self, db, agent_name, **kwargs):
            assert agent_name == "chat"

            return {
                "answer": "A normal chat response.",
                "sources": [],
                "plan": None,
            }

    with patch(
        "app.services.chat_service.get_session",
        return_value=FakeSession(session_id),
    ), patch(
        "app.services.chat_service.add_message",
        return_value=FakeMessage(
            session_id=session_id,
            role="assistant",
            content="A normal chat response.",
        ),
    ), patch(
        "app.services.chat_service.AgentDispatcher",
        return_value=FakeDispatcher(),
    ), patch(
        "app.services.chat_service.create_artifact",
    ) as create_artifact_mock:

        result = process_chat(
            db=db,
            session_id=session_id,
            message="What is product retention?",
            agent="chat",
        )

    create_artifact_mock.assert_not_called()

    assert result["answer"] == "A normal chat response."

    print("NORMAL CHAT NO ARTIFACT: PASSED")


def test_missing_session():
    db = FakeDB()

    with patch(
        "app.services.chat_service.get_session",
        return_value=None,
    ):

        try:
            process_chat(
                db=db,
                session_id=uuid4(),
                message="Write an essay.",
                agent="artifact",
            )

        except Exception as exc:
            assert str(exc) == "Session not found."
            print("MISSING SESSION: PASSED")
            return

    raise AssertionError(
        "Expected ChatServiceError"
    )


if __name__ == "__main__":
    print("=" * 70)
    print("PHASE 9 CHAT -> ARTIFACT PERSISTENCE TESTS")
    print("=" * 70)

    test_artifact_chat_persistence()
    test_non_artifact_chat_does_not_create_artifact()
    test_missing_session()

    print()
    print("ALL PHASE 9 CHAT ARTIFACT PERSISTENCE TESTS PASSED")

