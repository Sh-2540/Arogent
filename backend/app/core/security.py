"""
Auth primitives: password hashing, JWT creation/verification, and FastAPI
dependencies for "who is the current user" and "does this user have the
right role." Routers (Module 5) depend on these rather than implementing
auth logic themselves — keeps routes thin, per the layered architecture.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.core.enums import UserRole
from app.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_v1_prefix}/auth/login")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def _credentials_exception() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id_raw = payload.get("sub")
        if user_id_raw is None:
            raise _credentials_exception()
        user_id = int(user_id_raw)
    except (JWTError, ValueError) as e:
        raise _credentials_exception() from e

    user = db.get(User, user_id)
    if user is None:
        raise _credentials_exception()
    return user


def require_roles(*allowed_roles: UserRole):
    """
    Dependency factory for role-based access, e.g.:
        @router.post("/patients", dependencies=[Depends(require_roles(UserRole.ASHA))])

    Kept as a factory (not a single fixed dependency) so different routes
    can allow different role combinations without duplicating logic.
    """
    def _check(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role {current_user.role.value} is not permitted to perform this action.",
            )
        return current_user
    return _check
