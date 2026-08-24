from uuid import uuid4

from app.database import SessionLocal
from app.models import User
from app.services.chat_service import process_chat
from app.services.session_service import (
    create_session,
    get_session,
)


db = SessionLocal()

try:
    user = User(
        name="Chat Title Integration User",
        email=f"chat-title-{uuid4()}@test.local",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    session = create_session(
        db=db,
        user_id=user.id,
        title="New Chat",
    )

    message = "How can I improve product retention?"

    result = process_chat(
        db=db,
        session_id=session.id,
        message=message,
        agent="chat",
    )

    saved_session = get_session(
        db=db,
        session_id=session.id,
    )

    print()
    print("=" * 60)
    print("PHASE 10 CHAT TITLE INTEGRATION TEST")
    print("=" * 60)
    print(f"Session ID      : {session.id}")
    print(f"Original message: {message}")
    print(f"Database title  : {saved_session.title}")
    print("=" * 60)

    if saved_session.title == "Improve product retention":
        print("CHAT TITLE UPDATE: PASSED")
    else:
        print("CHAT TITLE UPDATE: FAILED")

    if result.get("answer"):
        print("CHAT RESPONSE: PASSED")
    else:
        print("CHAT RESPONSE: FAILED")

finally:
    db.close()
