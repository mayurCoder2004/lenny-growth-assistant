from uuid import UUID

from sqlalchemy.orm import Session

from app.agents.dispatcher import (
    AgentDispatcher,
    AgentDispatcherError,
)
from app.services.rag_service import answer_question
from app.services.session_service import add_message, get_session


class ChatServiceError(Exception):
    """Raised when the chat service fails."""


def process_chat(
    db: Session,
    session_id: UUID,
    message: str,
    agent: str = "chat",
) -> dict:
    """
    Process a chat message.

    Supported agents:

        chat
            -> Existing grounded RAG pipeline

        ship30
            -> Ship30 agent pipeline
    """

    if not message or not message.strip():
        raise ChatServiceError(
            "Message cannot be empty."
        )

    message = message.strip()

    if not agent or not agent.strip():
        raise ChatServiceError(
            "Agent cannot be empty."
        )

    agent = agent.strip().lower()

    session = get_session(
        db=db,
        session_id=session_id,
    )

    if session is None:
        raise ChatServiceError(
            "Session not found."
        )

    # Save user message first.
    add_message(
        db=db,
        session_id=session_id,
        role="user",
        content=message,
    )

    try:
        if agent == "chat":
            result = answer_question(
                db=db,
                question=message,
                top_k=5,
                distance_threshold=0.70,
            )

        else:
            dispatcher = AgentDispatcher()

            result = dispatcher.dispatch(
                db=db,
                agent_name=agent,
                message=message,
                session_id=session_id,
            )

    except AgentDispatcherError as exc:
        raise ChatServiceError(
            str(exc)
        ) from exc

    except Exception as exc:
        raise ChatServiceError(
            f"Failed to generate answer: {exc}"
        ) from exc

    answer = result.get(
        "answer",
        "",
    )

    if not answer:
        raise ChatServiceError(
            "Agent returned an empty answer."
        )

    answer = str(answer).strip()

    if not answer:
        raise ChatServiceError(
            "Agent returned an empty answer."
        )

    # Save assistant response.
    add_message(
        db=db,
        session_id=session_id,
        role="assistant",
        content=answer,
    )

    return {
        "answer": answer,
        "sources": result.get(
            "sources",
            [],
        ),
    }
