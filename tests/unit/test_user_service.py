import pytest
import uuid
from app.core.security import verify_password
from app.services.user_service import (
    create_user,
    authenticate,
    change_password,
    PasswordChangeError,
)

def test_password_change_logic(client):
    from app.db.session import SessionLocal

    db = SessionLocal()
    uid = uuid.uuid4().hex
    username = f"user_{uid}"
    email = f"user_{uid}@example.com"

    try:
        user = create_user(db, username, email, "Password123!")

        assert authenticate(db, username, "Password123!").id == user.id
        change_password(db, user, "Password123!", "NewPassword123!")
        db.refresh(user)
        assert verify_password("NewPassword123!", user.hashed_password)

        with pytest.raises(PasswordChangeError):
            change_password(db, user, "wrong", "AnotherPass123!")

    finally:
        db.close()
