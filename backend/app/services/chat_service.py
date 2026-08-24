from uuid import UUID

from sqlalchemy.orm import Session

from app.services.rag_service import answer_question
from app.services.session_service import add_message, get_session


class ChatServiceError(Exception):
    """Raised when the chat service fails."""


def process_chat(
    db: Session,
    session_id: UUID,
    message: str,
) -> dict:
    """
    Process a chat message through the RAG pipeline.

    Flow:
        User message
            ?
        Persist user message
            ?
        RAG answer generation
            ?
        Persist assistant message
            ?
        Return answer + sources
    """

    if not message or not message.strip():
        raise ChatServiceError("Message cannot be empty.")

    message = message.strip()

    session = get_session(
        db=db,
        session_id=session_id,
    )

    if session is None:
        raise ChatServiceError("Session not found.")

    # Save user message first.
    add_message(
        db=db,
        session_id=session_id,
        role="user",
        content=message,
    )

    try:
        result = answer_question(
            db=db,
            question=message,
            top_k=5,
            distance_threshold=0.70,
        )
    except Exception as exc:
        raise ChatServiceError(
            f"Failed to generate answer: {exc}"
        ) from exc

    answer = result.get("answer", "").strip()

    if not answer:
        raise ChatServiceError(
            "RAG pipeline returned an empty answer."
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
        "sources": result.get("sources", []),
    }
