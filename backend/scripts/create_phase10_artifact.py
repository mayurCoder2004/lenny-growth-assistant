from uuid import uuid4

from app.database import SessionLocal
from app.models import User
from app.services.artifact_service import create_artifact
from app.services.session_service import create_session


db = SessionLocal()

try:
    user = User(
        name="Phase 10 Frontend User",
        email=f"phase10-frontend-{uuid4()}@test.local",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    session = create_session(
        db=db,
        user_id=user.id,
        title="Phase 10 Frontend Integration",
    )

    artifact = create_artifact(
        db=db,
        session_id=session.id,
        message_id=None,
        artifact_type="essay",
        title="Frontend API Integration Test",
        content=(
            "This artifact was loaded from the real FastAPI "
            "backend and persisted in PostgreSQL."
        ),
    )

    print()
    print("PHASE 10 REAL ARTIFACT")
    print("=" * 50)
    print(f"Artifact ID: {artifact.id}")
    print(f"Session ID:  {session.id}")
    print("=" * 50)
    print()

finally:
    db.close()
