from app.database import SessionLocal
from app.models import User
from app.services.chat_service import process_chat
from app.services.session_service import create_session


USER_EMAIL = "demo@lenny.local"


def main():
    db = SessionLocal()

    try:
        user = (
            db.query(User)
            .filter(User.email == USER_EMAIL)
            .first()
        )

        if user is None:
            raise RuntimeError(
                f"Demo user not found: {USER_EMAIL}"
            )

        session = create_session(
            db=db,
            user_id=user.id,
            title="Phase 6 Automated Test",
        )

        result = process_chat(
            db=db,
            session_id=session.id,
            message="How should I think about leaving my job?",
        )

        assert result["answer"].strip()
        assert isinstance(result["sources"], list)
        assert len(result["sources"]) > 0

        print("=" * 70)
        print("PHASE 6 CHAT SERVICE TEST")
        print("=" * 70)

        print("\nSession:")
        print(session.id)

        print("\nAnswer:")
        print(result["answer"])

        print("\nSources:")
        for index, source in enumerate(
            result["sources"],
            start=1,
        ):
            print(
                f"{index}. "
                f"{source.get('guest')} | "
                f"distance={source.get('distance')}"
            )

        print("\n" + "=" * 70)
        print("PHASE 6 CHAT SERVICE TEST: PASSED")
        print("=" * 70)

    finally:
        db.close()


if __name__ == "__main__":
    main()
