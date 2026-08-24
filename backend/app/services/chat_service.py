from uuid import UUID

from sqlalchemy.orm import Session

from app.agents.dispatcher import (
    AgentDispatcher,
    AgentDispatcherError,
)
from app.services.artifact_service import (
    ArtifactServiceError,
    create_artifact,
)
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
    Process a chat message through the application agent layer.

    Supported agents:

        chat
            -> ChatAgent
            -> Existing grounded RAG pipeline

        ship30
            -> Ship30Agent
            -> Grounded Ship30 planning pipeline

        artifact
            -> ArtifactAgent
            -> Grounded Ship30 writing pipeline
            -> Persisted Artifact
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

    # Save assistant response and retain the persisted
    # message so artifact records can reference it.
    assistant_message = add_message(
        db=db,
        session_id=session_id,
        role="assistant",
        content=answer,
    )

    # Track the generated artifact ID for artifact requests.
    artifact_id = None

    # Persist generated artifacts.
    if agent == "artifact":
        try:
            artifact = create_artifact(
                db=db,
                session_id=session_id,
                message_id=assistant_message.id,
                artifact_type="essay",
                title="Ship30 Essay",
                content=answer,
            )

            artifact_id = artifact.id

        except ArtifactServiceError as exc:
            raise ChatServiceError(
                str(exc)
            ) from exc

        except Exception as exc:
            raise ChatServiceError(
                f"Failed to persist artifact: {exc}"
            ) from exc

    return {
        "answer": answer,
        "sources": result.get(
            "sources",
            [],
        ),
        "plan": result.get(
            "plan",
        ),
        "artifact_id": artifact_id,
    }
