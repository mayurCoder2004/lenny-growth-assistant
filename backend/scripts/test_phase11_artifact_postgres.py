from uuid import uuid4

from app.database import SessionLocal
from app.models import Artifact, Session, User
from app.services.artifact_service import create_artifact


db = SessionLocal()

user = None
session = None

try:
    user = User(
        name="Phase 11 Test User",
        email=f"phase11-{uuid4()}@example.com",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    session = Session(
        user_id=user.id,
        title="Phase 11 Sanitization Test",
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    malicious_content = """
    <h1>Growth Strategy</h1>
    <p>This is <strong>safe</strong> content.</p>

    <script>alert("xss")</script>

    <img src="x" onerror="alert(1)">

    <p onclick="alert(2)">
        Another paragraph
    </p>

    <a href="javascript:alert(3)">
        Malicious link
    </a>

    <a href="https://example.com" title="Safe">
        Safe link
    </a>
    """

    artifact = create_artifact(
        db=db,
        session_id=session.id,
        message_id=None,
        artifact_type="essay",
        title="Phase 11 Security Test",
        content=malicious_content,
    )

    persisted = db.get(Artifact, artifact.id)

    assert persisted is not None

    result = persisted.content

    assert "<script" not in result
    assert "<img" not in result
    assert "onerror" not in result
    assert "onclick" not in result
    assert "javascript:" not in result

    assert "<h1>Growth Strategy</h1>" in result
    assert "<p>This is <strong>safe</strong> content.</p>" in result
    assert 'href="https://example.com"' in result

    print("=" * 70)
    print("PHASE 11 REAL POSTGRESQL ARTIFACT TEST")
    print("=" * 70)
    print()
    print("Artifact ID:")
    print(artifact.id)
    print()
    print("Persisted sanitized content:")
    print(result)
    print()
    print("REAL POSTGRESQL ARTIFACT SANITIZATION TEST PASSED")

finally:
    if session is not None:
        db.delete(session)
        db.commit()

    if user is not None:
        db.delete(user)
        db.commit()

    db.close()

    print()
    print("TEST DATA CLEANED UP")
