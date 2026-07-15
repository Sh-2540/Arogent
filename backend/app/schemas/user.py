"""Pydantic schemas for User — request/response shapes for auth endpoints (Module 5)."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.core.enums import UserRole


class UserCreate(BaseModel):
    full_name: str
    username: str
    password: str
    role: UserRole
    assigned_village: str | None = None


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    username: str
    role: UserRole
    assigned_village: str | None
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead
