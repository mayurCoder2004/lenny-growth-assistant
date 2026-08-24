from unittest.mock import Mock
from uuid import uuid4

from app.models import Artifact
from app.services.artifact_service import (
    ArtifactServiceError,
    create_artifact,
    get_artifact,
)


class FakeDB:
    def __init__(self):
        self.added = None
        self.refreshed = None
        self.committed = False

    def add(self, value):
        self.added = value

    def commit(self):
        self.committed = True

    def refresh(self, value):
        self.refreshed = value

    def get(self, model, artifact_id):
        if model is Artifact and self.added is not None:
            if self.added.id == artifact_id:
                return self.added

        return None


def test_create_artifact():
    db = FakeDB()

    session_id = uuid4()
    message_id = uuid4()

    artifact = create_artifact(
        db=db,
        session_id=session_id,
        message_id=message_id,
        artifact_type="essay",
        title="Improving Onboarding",
        content="A grounded essay.",
    )

    assert isinstance(artifact, Artifact)
    assert artifact.session_id == session_id
    assert artifact.message_id == message_id
    assert artifact.type == "essay"
    assert artifact.title == "Improving Onboarding"
    assert artifact.content == "A grounded essay."

    assert db.added is artifact
    assert db.committed is True
    assert db.refreshed is artifact

    print("ARTIFACT CREATE: PASSED")


def test_get_artifact():
    db = FakeDB()

    session_id = uuid4()

    artifact = create_artifact(
        db=db,
        session_id=session_id,
        message_id=None,
        artifact_type="essay",
        title="Test",
        content="Content",
    )

    result = get_artifact(
        db=db,
        artifact_id=artifact.id,
    )

    assert result is artifact

    print("ARTIFACT GET: PASSED")


def test_empty_title():
    db = FakeDB()

    try:
        create_artifact(
            db=db,
            session_id=uuid4(),
            message_id=None,
            artifact_type="essay",
            title="",
            content="Content",
        )
    except ArtifactServiceError as exc:
        assert "title cannot be empty" in str(exc)
        print("ARTIFACT EMPTY TITLE: PASSED")
        return

    raise AssertionError(
        "Expected ArtifactServiceError"
    )


def test_empty_content():
    db = FakeDB()

    try:
        create_artifact(
            db=db,
            session_id=uuid4(),
            message_id=None,
            artifact_type="essay",
            title="Test",
            content="",
        )
    except ArtifactServiceError as exc:
        assert "content cannot be empty" in str(exc)
        print("ARTIFACT EMPTY CONTENT: PASSED")
        return

    raise AssertionError(
        "Expected ArtifactServiceError"
    )


def test_requires_database():
    try:
        create_artifact(
            db=None,
            session_id=uuid4(),
            message_id=None,
            artifact_type="essay",
            title="Test",
            content="Content",
        )
    except ArtifactServiceError as exc:
        assert "database session is required" in str(exc)
        print("ARTIFACT DATABASE REQUIREMENT: PASSED")
        return

    raise AssertionError(
        "Expected ArtifactServiceError"
    )


if __name__ == "__main__":
    print("=" * 70)
    print("PHASE 9 ARTIFACT SERVICE TESTS")
    print("=" * 70)

    test_create_artifact()
    test_get_artifact()
    test_empty_title()
    test_empty_content()
    test_requires_database()

    print()
    print("ALL PHASE 9 ARTIFACT SERVICE TESTS PASSED")
