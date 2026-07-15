"""Schemas internal to Arogent Risk."""
from __future__ import annotations

from pydantic import BaseModel

from app.core.enums import RiskLevel


class RiskInput(BaseModel):
    age: int
    bmi: float
    blood_glucose_mg_dl: float
    family_history_diabetes: bool
    physical_activity_level: str
    symptoms: list[str]


class FeatureContribution(BaseModel):
    feature: str
    display_name: str
    contribution: float
    """Signed for Logistic Regression (positive = increases risk, negative =
    decreases it); magnitude-only (unsigned global importance) if the
    deployed model is ever XGBoost — see app/risk/features.py."""
    direction: str  # "increases_risk" | "decreases_risk" | "unspecified"


class RiskResult(BaseModel):
    risk_score: float  # 0-100
    risk_level: RiskLevel
    model_used: str
    top_contributing_features: list[FeatureContribution]
