from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.user import User
from app.core.security import hash_password, verify_password

class UserAlreadyExists(Exception):
    pass

class InvalidCredentials(Exception):
    pass

class PasswordChangeError(Exception):
    pass

def get_user_by_username(db: Session, username: str) -> User | None:
    return db.execute(select(User).where(User.username == username)).scalar_one_or_none()

def get_user_by_email(db: Session, email: str) -> User | None:
    return db.execute(select(User).where(User.email == email)).scalar_one_or_none()

def get_user(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)

def create_user(db: Session, username: str, email: str, password: str) -> User:
    if get_user_by_username(db, username) or get_user_by_email(db, email):
        raise UserAlreadyExists("Username or email already exists")

    user = User(username=username, email=email, hashed_password=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate(db: Session, username: str, password: str) -> User:
    user = get_user_by_username(db, username)
    if not user or not verify_password(password, user.hashed_password):
        raise InvalidCredentials("Invalid username or password")
    return user

def update_profile(db: Session, user: User, username: str, email: str) -> User:
    # If changing to an existing username/email, reject
    if username != user.username and get_user_by_username(db, username):
        raise UserAlreadyExists("Username already exists")
    if email != user.email and get_user_by_email(db, email):
        raise UserAlreadyExists("Email already exists")

    user.username = username
    user.email = email
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def change_password(db: Session, user: User, current_password: str, new_password: str) -> None:
    if not verify_password(current_password, user.hashed_password):
        raise PasswordChangeError("Current password is incorrect")
    user.hashed_password = hash_password(new_password)
    db.add(user)
    db.commit()
