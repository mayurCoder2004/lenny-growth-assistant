from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.database import SessionLocal
from app.models import User
from app.services.artifact_service import create_artifact
from app.services.session_service import create_session


client = TestClient(app)


def test_artifact_retrieval():
    db = SessionLocal()

    artifact = None
    session = None
    user = None

    try:
        user = User(
            name="Phase 9 Test User",
            email=f"phase9-{uuid4()}@test.local",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        session = create_session(
            db=db,
            user_id=user.id,
            title="Phase 9 Artifact Test",
        )

        artifact = create_artifact(
            db=db,
            session_id=session.id,
            message_id=None,
            artifact_type="essay",
            title="Phase 9 Test Essay",
            content="This is a persisted artifact used for API verification.",
        )

        response = client.get(
            f"/artifacts/{artifact.id}"
        )

        assert response.status_code == 200

        data = response.json()

        assert data["id"] == str(artifact.id)
        assert data["session_id"] == str(session.id)
        assert data["message_id"] is None
        assert data["type"] == "essay"
        assert data["title"] == "Phase 9 Test Essay"
        assert (
            data["content"]
            == "This is a persisted artifact used for API verification."
        )

        print("ARTIFACT GET 200: PASSED")

    finally:
        if user is not None:
            db.delete(user)
            db.commit()

        db.close()


def test_artifact_not_found():
    artifact_id = uuid4()

    response = client.get(
        f"/artifacts/{artifact_id}"
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == "Artifact not found."

    print("ARTIFACT GET 404: PASSED")


if __name__ == "__main__":
    print("=" * 70)
    print("PHASE 9 ARTIFACT API TESTS")
    print("=" * 70)

    test_artifact_retrieval()
    test_artifact_not_found()

    print()
    print("ALL PHASE 9 ARTIFACT API TESTS PASSED")
