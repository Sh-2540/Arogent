"""
Arogent Risk — Diabetes Risk Prediction.

Only ever runs on screenings that Arogent Verify marked HIGH confidence —
see service.py's docstring for where and how that rule is enforced.

Public API:
    run_risk_prediction_for_screening(db, screening) -> RiskResult | None
    predict_diabetes_risk(risk_input, confidence_status) -> RiskResult
"""
from app.risk.service import (
    run_risk_prediction_for_screening,
    predict_diabetes_risk,
    determine_risk_level,
    ConfidenceGateError,
)
from app.risk.schemas import RiskInput, RiskResult, FeatureContribution

__all__ = [
    "run_risk_prediction_for_screening",
    "predict_diabetes_risk",
    "determine_risk_level",
    "ConfidenceGateError",
    "RiskInput",
    "RiskResult",
    "FeatureContribution",
]
