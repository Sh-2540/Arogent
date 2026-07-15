"""Auth service — business logic for registration and login, kept out of
the router per the thin-routes architecture."""
from __future__ import annotations

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User
from app.schemas.user import UserCreate


class UsernameAlreadyExistsError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


def register_user(db: Session, data: UserCreate) -> User:
    user = User(
        full_name=data.full_name,
        username=data.username,
        hashed_password=hash_password(data.password),
        role=data.role,
        assigned_village=data.assigned_village,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise UsernameAlreadyExistsError(f"Username {data.username!r} is already taken.") from e
    db.refresh(user)
    return user


def authenticate_user(db: Session, username: str, password: str) -> tuple[User, str]:
    user = db.query(User).filter(User.username == username).one_or_none()
    if user is None or not verify_password(password, user.hashed_password):
        raise InvalidCredentialsError("Incorrect username or password.")
    token = create_access_token(user.id)
    return user, token
