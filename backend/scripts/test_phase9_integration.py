from unittest.mock import patch
from uuid import uuid4

from app.database import SessionLocal
from app.models import Artifact, User
from app.services.chat_service import process_chat
from app.services.session_service import create_session
from app.skills.ship30_skill import Ship30Essay


def test_end_to_end_artifact_persistence():
    db = SessionLocal()

    user = None

    try:
        user = User(
            name="Phase 9 Integration User",
            email=f"phase9-integration-{uuid4()}@test.local",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        session = create_session(
            db=db,
            user_id=user.id,
            title="Phase 9 Integration Test",
        )

        with patch(
            "app.services.ship30_skill_service.Ship30SkillService.generate"
        ) as generate_mock:

            generate_mock.return_value = Ship30Essay(
                content="A grounded integration-test essay.",
                evidence_ids=["evidence-1"],
            )

            result = process_chat(
                db=db,
                session_id=session.id,
                message="Write an essay about product retention.",
                agent="artifact",
            )

        assert result["answer"] == (
            "A grounded integration-test essay."
        )

        generate_mock.assert_called_once()

        artifact = (
            db.query(Artifact)
            .filter(
                Artifact.session_id == session.id
            )
            .first()
        )

        assert artifact is not None

        assert artifact.type == "essay"

        assert artifact.title == "Ship30 Essay"

        assert artifact.content == (
            "A grounded integration-test essay."
        )

        assert artifact.message_id is not None

        print("ARTIFACT CHAT GENERATION: PASSED")
        print("SHIP30 SERVICE INVOCATION: PASSED")
        print("ARTIFACT DATABASE PERSISTENCE: PASSED")
        print("ARTIFACT CONTENT: PASSED")
        print("ARTIFACT MESSAGE LINK: PASSED")

    finally:
        if user is not None:
            db.delete(user)
            db.commit()

        db.close()


if __name__ == "__main__":
    print("=" * 70)
    print("PHASE 9 END-TO-END ARTIFACT TEST")
    print("=" * 70)

    test_end_to_end_artifact_persistence()

    print()
    print("ALL PHASE 9 END-TO-END TESTS PASSED")
