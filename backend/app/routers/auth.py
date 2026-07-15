"""Auth routes — registration and login. Business logic lives in
app.services.auth_service; this file only translates HTTP <-> service calls."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import UserCreate, UserRead, Token
from app.services.auth_service import register_user, authenticate_user, UsernameAlreadyExistsError, InvalidCredentialsError

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description=(
        "Registers a new ASHA worker, PHC officer, or District Health Officer. "
        "In production this would itself be an admin-only action; for the "
        "hackathon MVP it's open so the demo can seed its own accounts."
    ),
    responses={409: {"description": "Username already taken"}},
)
def register(data: UserCreate, db: Session = Depends(get_db)) -> UserRead:
    try:
        user = register_user(db, data)
    except UsernameAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e
    return UserRead.model_validate(user)


@router.post(
    "/login",
    response_model=Token,
    summary="Log in and receive an access token",
    description="Exchanges a username/password for a bearer token used on all other endpoints.",
    responses={401: {"description": "Incorrect username or password"}},
)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> Token:
    try:
        user, token = authenticate_user(db, form_data.username, form_data.password)
    except InvalidCredentialsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
    return Token(access_token=token, user=UserRead.model_validate(user))
