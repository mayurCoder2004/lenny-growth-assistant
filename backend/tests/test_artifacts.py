import uuid

import pytest

from app.services.artifact_service import (
    ArtifactServiceError,
    create_artifact,
)


def test_artifact_creation_persists_correctly(fake_db):
    artifact = create_artifact(
        db=fake_db,
        session_id=uuid.uuid4(),
        message_id=uuid.uuid4(),
        artifact_type="essay",
        title="Ship30 Essay",
        content="<h1>Activation</h1><p>Help users find value.</p>",
    )

    assert fake_db.get(type(artifact), artifact.id) is artifact
    assert artifact.type == "essay"
    assert artifact.title == "Ship30 Essay"


def test_artifact_content_is_sanitized(fake_db):
    artifact = create_artifact(
        db=fake_db,
        session_id=uuid.uuid4(),
        message_id=None,
        artifact_type="essay",
        title="Security Test",
        content=(
            "<h1>Safe</h1><script>alert(1)</script>"
            "<a href=\"javascript:alert(2)\">bad</a>"
            "<a href=\"https://example.com\">good</a>"
        ),
    )

    assert "<script" not in artifact.content
    assert "javascript:" not in artifact.content
    assert 'href="https://example.com"' in artifact.content


def test_empty_artifact_content_is_rejected(fake_db):
    with pytest.raises(ArtifactServiceError) as exc_info:
        create_artifact(
            db=fake_db,
            session_id=uuid.uuid4(),
            message_id=None,
            artifact_type="essay",
            title="Empty",
            content="",
        )

    assert "content cannot be empty" in str(exc_info.value)
