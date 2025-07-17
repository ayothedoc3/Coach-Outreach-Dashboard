from app.database import SessionLocal, engine
from app.models import User
from app.crud import pwd_context
from datetime import datetime

db = SessionLocal()

# Check if user already exists
existing_user = db.query(User).filter(User.email == "admin@example.com").first()

if not existing_user:
    hashed_password = pwd_context.hash("admin")
    new_user = User(
        username="admin",
        email="admin@example.com",
        password_hash=hashed_password,
        is_active=True,
        created_at=datetime.utcnow()
    )
    db.add(new_user)
    db.commit()
    print("Admin user created successfully.")
else:
    print("Admin user already exists.")

db.close()
