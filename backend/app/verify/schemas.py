"""
Schemas internal to Arogent Verify.

VerifyInput carries both the submitted screening data and the surrounding
context (prior screenings, ASHA's assignment) that the consistency signals
need — service.py assembles this from the DB before the pipeline runs, so
every downstream stage (rules, historical, geographic, anomaly, aggregate)
is a pure function that never touches the database itself.
"""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.core.enums import ConfidenceStatus


class PriorScreening(BaseModel):
    """Minimal projection of a past Screening row — just what the
    consistency signals need, not the full record."""
    blood_glucose_mg_dl: float
    bmi: float
    village_at_screening: str
    screened_at: datetime


class VerifyInput(BaseModel):
    # Submitted with the screening form
    patient_id: int
    blood_glucose_mg_dl: float
    bmi: float
    family_history_diabetes: bool
    physical_activity_level: str
    symptoms: list[str]
    village_at_screening: str
    latitude: float | None
    longitude: float | None
    screened_at: datetime

    # Assembled by service.py from the DB — never submitted by the client
    recorded_by_id: int
    asha_assigned_village: str
    patient_previous_screenings: list[PriorScreening]
    asha_screenings_today: list[PriorScreening]


class SignalResult(BaseModel):
    """The output of a single consistency signal — a score, whether the
    signal was even computable (vs. defaulted due to missing data), and
    zero or more flags used later by explain.py."""
    score: float  # 0-100
    available: bool
    flags: list[str] = []


class ConfidenceBreakdown(BaseModel):
    """Always fully populated for display, even when a signal was
    unavailable and excluded from the weighted average — in that case it
    shows the neutral score, and `hard_bound_violation` / `explanation`
    communicate the caveat instead of leaving a gap in the UI."""
    clinical_consistency_score: float
    historical_consistency_score: float
    behaviour_consistency_score: float
    geographic_consistency_score: float


class VerifyResult(BaseModel):
    confidence_score: float
    status: ConfidenceStatus
    signals: ConfidenceBreakdown
    recommendation: str
    explanation: list[str]
    hard_bound_violation: bool
