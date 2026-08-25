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
from app.services.session_service import (
    add_message,
    get_messages,
    get_session,
    update_session_title,
)


class ChatServiceError(Exception):
    """Raised when the chat service fails."""


def generate_session_title(message: str) -> str:
    """
    Generate a short human-readable title from the
    user's first message.
    """

    cleaned = " ".join(message.strip().split())

    if not cleaned:
        return "New Chat"

    # Remove common question prefixes.
    prefixes = (
        "how can i ",
        "how do i ",
        "how to ",
        "can you ",
        "could you ",
        "please ",
        "i want to ",
        "i need to ",
        "help me ",
        "write ",
    )

    title = cleaned.lower()

    for prefix in prefixes:
        if title.startswith(prefix):
            title = title[len(prefix):]
            break

    if not title:
        title = cleaned

    # Clean up trailing punctuation.
    title = title.rstrip("?.!,:;")

    # Capitalize the first character.
    title = title[0].upper() + title[1:]

    # Keep common product terms properly capitalized.
    replacements = {
        "saas": "SaaS",
        "ai": "AI",
        "api": "API",
        "mvp": "MVP",
        "ux": "UX",
        "ui": "UI",
    }

    words = title.split()
    title = " ".join(
        replacements.get(word.lower(), word)
        for word in words
    )

    # Keep titles short.
    if len(title) > 60:
        title = title[:60].rsplit(" ", 1)[0]

    return title


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

    # Check whether this is the first user message.
    existing_messages = get_messages(
        db=db,
        session_id=session_id,
    )

    is_first_message = len(existing_messages) == 0

    # Save user message first.
    add_message(
        db=db,
        session_id=session_id,
        role="user",
        content=message,
    )

    # Automatically name a newly created conversation.
    if is_first_message and session.title == "New Chat":
        update_session_title(
            db=db,
            session_id=session_id,
            title=generate_session_title(message),
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
        sources=result.get("sources", []),
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

