from app.database import SessionLocal
from app.models import User

db = SessionLocal()

try:
    users = db.query(User).order_by(User.created_at.desc()).limit(10).all()

    for user in users:
        print(f"{user.id} | {user.name} | {user.email}")

finally:
    db.close()
