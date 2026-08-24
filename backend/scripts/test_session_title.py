from uuid import uuid4

from app.database import SessionLocal
from app.models import User
from app.services.chat_service import generate_session_title
from app.services.session_service import (
    create_session,
    get_session,
)


db = SessionLocal()

try:
    user = User(
        name="Title Test User",
        email=f"title-test-{uuid4()}@test.local",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    session = create_session(
        db=db,
        user_id=user.id,
        title="New Chat",
    )

    message = "How can I improve activation for my SaaS?"

    generated_title = generate_session_title(message)

    session.title = generated_title
    db.commit()
    db.refresh(session)

    saved_session = get_session(
        db=db,
        session_id=session.id,
    )

    print()
    print("=" * 60)
    print("PHASE 10 SESSION TITLE TEST")
    print("=" * 60)
    print(f"Original message : {message}")
    print(f"Generated title  : {generated_title}")
    print(f"Database title   : {saved_session.title}")
    print("=" * 60)

    if saved_session.title == "Improve activation for my SaaS":
        print("SESSION TITLE PERSISTENCE: PASSED")
    else:
        print("SESSION TITLE PERSISTENCE: FAILED")

finally:
    db.close()
