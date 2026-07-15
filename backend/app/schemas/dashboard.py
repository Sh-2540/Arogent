"""Schemas for the District Dashboard (data source for Module 9)."""
from __future__ import annotations

from pydantic import BaseModel


class StatusCount(BaseModel):
    status: str
    count: int


class VillageSummary(BaseModel):
    village: str
    total_screenings: int
    high_risk_count: int
    needs_review_count: int
    average_confidence_score: float


class DashboardSummary(BaseModel):
    total_screenings: int
    screenings_by_confidence_status: list[StatusCount]
    screenings_by_risk_level: list[StatusCount]
    pending_referrals_count: int
    village_summaries: list[VillageSummary]
