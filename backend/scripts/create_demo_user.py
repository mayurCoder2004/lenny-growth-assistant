import os
from uuid import UUID

from app.database import SessionLocal
from app.models import User


DEFAULT_DEMO_USER_ID = "32f8bbc3-60fb-4995-8473-9ff1d14ce88e"


def main() -> None:
    db = SessionLocal()

    try:
        user_id = UUID(
            os.environ.get(
                "DEMO_USER_ID",
                DEFAULT_DEMO_USER_ID,
            )
        )

        existing_user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        if existing_user:
            print(f"Demo user already exists: {existing_user.id}")
            return

        user = User(
            id=user_id,
            name="Phase 10 Frontend User",
            email="demo@lenny.local",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        print(f"Demo user created: {user.id}")

    finally:
        db.close()


if __name__ == "__main__":
    main()
