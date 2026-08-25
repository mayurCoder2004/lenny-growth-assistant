from uuid import UUID

from sqlalchemy.orm import Session

from app.models import Artifact
from app.services.html_sanitizer import sanitize_html


class ArtifactServiceError(Exception):
    """Raised when artifact persistence fails."""


def create_artifact(
    db: Session,
    session_id: UUID,
    message_id: UUID | None,
    artifact_type: str,
    title: str,
    content: str,
) -> Artifact:
    if db is None:
        raise ArtifactServiceError(
            "A database session is required."
        )

    if not session_id:
        raise ArtifactServiceError(
            "Session ID is required."
        )

    if not artifact_type or not artifact_type.strip():
        raise ArtifactServiceError(
            "Artifact type cannot be empty."
        )

    if not title or not title.strip():
        raise ArtifactServiceError(
            "Artifact title cannot be empty."
        )

    if not content or not content.strip():
        raise ArtifactServiceError(
            "Artifact content cannot be empty."
        )

    sanitized_content = sanitize_html(content)

    if not sanitized_content.strip():
        raise ArtifactServiceError(
            "Artifact content is empty after sanitization."
        )

    artifact = Artifact(
        session_id=session_id,
        message_id=message_id,
        type=artifact_type.strip(),
        title=title.strip(),
        content=sanitized_content.strip(),
    )

    db.add(artifact)
    db.commit()
    db.refresh(artifact)

    return artifact


def get_artifact(
    db: Session,
    artifact_id: UUID,
    session_id: UUID | None = None,
) -> Artifact | None:
    if db is None:
        raise ArtifactServiceError(
            "A database session is required."
        )

    artifact = db.get(Artifact, artifact_id)

    if artifact is None:
        return None

    if session_id is not None and artifact.session_id != session_id:
        return None

    return artifact
