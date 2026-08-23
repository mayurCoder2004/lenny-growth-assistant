from app.database import SessionLocal
from app.models import User


def main() -> None:
    db = SessionLocal()

    try:
        existing_user = (
            db.query(User)
            .filter(User.email == "demo@lenny.local")
            .first()
        )

        if existing_user:
            print(f"Demo user already exists: {existing_user.id}")
            return

        user = User(
            name="Demo User",
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