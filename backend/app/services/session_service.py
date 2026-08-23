from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Message, Session as ChatSession, User


def get_user(
    db: Session,
    user_id: UUID,
) -> User | None:
    return db.get(User, user_id)


def create_session(
    db: Session,
    user_id: UUID,
    title: str,
) -> ChatSession:
    session = ChatSession(
        user_id=user_id,
        title=title,
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return session


def get_session(
    db: Session,
    session_id: UUID,
) -> ChatSession | None:
    return db.get(ChatSession, session_id)


def add_message(
    db: Session,
    session_id: UUID,
    role: str,
    content: str,
) -> Message:
    message = Message(
        session_id=session_id,
        role=role,
        content=content,
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return message


def get_messages(
    db: Session,
    session_id: UUID,
) -> list[Message]:
    statement = (
        select(Message)
        .where(Message.session_id == session_id)
        .order_by(Message.created_at)
    )

    return list(db.scalars(statement).all())