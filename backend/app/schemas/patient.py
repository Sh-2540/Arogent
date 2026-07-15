"""Pydantic schemas for Patient — the Register Patient screen (Module 7)."""
from datetime import datetime, date

from pydantic import BaseModel, ConfigDict, Field


class PatientCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=150)
    age: int = Field(ge=0, le=120)
    gender: str
    village: str = Field(min_length=1, max_length=120)
    phone_number: str | None = None
    date_of_birth: date | None = None


class PatientRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    age: int
    gender: str
    village: str
    phone_number: str | None
    date_of_birth: date | None
    registered_by_id: int
    registered_at: datetime


class PatientSummary(BaseModel):
    """Lightweight shape used in lists (e.g. patient search/autocomplete)."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    age: int
    village: str
