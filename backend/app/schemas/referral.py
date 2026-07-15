"""Pydantic schemas for Referral — the tangible record shown on the Result screen."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.core.enums import ReferralStatus


class ReferralRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: int
    screening_id: int
    phc: str
    priority: str
    reason: str
    status: ReferralStatus
    generated_at: datetime


class ReferralStatusUpdate(BaseModel):
    status: ReferralStatus
