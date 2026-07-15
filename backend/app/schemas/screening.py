"""
Pydantic schemas for Screening.

Split into three shapes matching the three moments they're used:
  - ScreeningCreate: what the Screening Form (Module 8) submits
  - ConfidenceBreakdown: the four Arogent Verify signal sub-scores,
    nested inside the result so the UI can show the full breakdown
    from Section 5 of the proposal, not just the final number
  - ScreeningResult: the full Result Screen (Module 8) payload
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import ConfidenceStatus, RiskLevel, ReferralStatus


class ScreeningCreate(BaseModel):
    patient_id: int
    blood_glucose_mg_dl: float = Field(gt=0, le=1000)
    bmi: float = Field(gt=0, le=100)
    family_history_diabetes: bool = False
    physical_activity_level: str = Field(pattern="^(LOW|MODERATE|HIGH)$")
    symptoms: list[str] = Field(default_factory=list)
    village_at_screening: str
    latitude: float | None = None
    longitude: float | None = None


class ConfidenceBreakdown(BaseModel):
    """The four consistency signals behind Arogent Verify's final score,
    weighted 35 / 30 / 20 / 15 as documented in the proposal."""
    clinical_consistency_score: float
    historical_consistency_score: float
    behaviour_consistency_score: float
    geographic_consistency_score: float


class ScreeningResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: int
    screened_at: datetime

    # Raw inputs, echoed back for the Result screen
    blood_glucose_mg_dl: float
    bmi: float

    # Arogent Verify output
    confidence_score: float | None
    confidence_status: ConfidenceStatus | None
    confidence_breakdown: ConfidenceBreakdown | None = None
    confidence_reasons: list[str]

    # Arogent Risk output — null when confidence was too low to generate one
    risk_score: float | None
    risk_level: RiskLevel | None

    # Referral
    referral_status: ReferralStatus | None

    recommendation: str
    """Human-readable next step, e.g. 'Refer to PHC' or 'Repeat screening'."""


class ScreeningSummary(BaseModel):
    """Lightweight shape used in patient history lists and the district dashboard feed."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: int
    screened_at: datetime
    confidence_status: ConfidenceStatus | None
    risk_level: RiskLevel | None
