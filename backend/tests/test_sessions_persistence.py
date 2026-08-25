import uuid

from app.models import User
from app.services.session_service import (
    add_message,
    create_session,
    get_messages,
    get_session,
)


def test_create_and_retrieve_session(fake_db):
    user = User(
        id=uuid.uuid4(),
        name="Test User",
        email="test@example.com",
    )
    fake_db.add(user)

    session = create_session(
        db=fake_db,
        user_id=user.id,
        title="Activation Research",
    )

    retrieved = get_session(fake_db, session.id)

    assert retrieved is session
    assert retrieved.title == "Activation Research"
    assert retrieved.user_id == user.id


def test_add_and_retrieve_messages_preserves_sources(fake_db):
    session_id = uuid.uuid4()
    sources = [
        {
            "evidence_id": "source-1-0",
            "source_id": "source-1",
            "guest": "Ada Chen Rekhi",
            "title": "Finding Product-Market Fit",
            "url": "https://example.com/ada",
        }
    ]

    add_message(
        db=fake_db,
        session_id=session_id,
        role="user",
        content="How do I improve activation?",
    )
    add_message(
        db=fake_db,
        session_id=session_id,
        role="assistant",
        content="Improve onboarding around fast value.",
        sources=sources,
    )

    messages = get_messages(fake_db, session_id)

    assert [message.role for message in messages] == [
        "user",
        "assistant",
    ]
    assert messages[1].sources == sources


def test_sessions_remain_independent(fake_db):
    session_a = uuid.uuid4()
    session_b = uuid.uuid4()

    add_message(fake_db, session_a, "user", "Question A")
    add_message(fake_db, session_b, "user", "Question B")
    add_message(fake_db, session_a, "assistant", "Answer A")

    messages_a = get_messages(fake_db, session_a)
    messages_b = get_messages(fake_db, session_b)

    assert [message.content for message in messages_a] == [
        "Question A",
        "Answer A",
    ]
    assert [message.content for message in messages_b] == [
        "Question B",
    ]
