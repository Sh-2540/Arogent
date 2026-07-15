"""
Arogent Verify — Screening Quality Intelligence.

Estimates a Screening Confidence Score from four consistency signals
before any diabetes risk prediction is generated. See service.py for the
orchestration and each signal module (rules, historical, anomaly,
geographic) for the individual algorithms.

Public API:
    verify_screening(db, screening_data, recorded_by_id) -> (Screening, VerifyResult)
"""
from app.verify.service import verify_screening, build_verify_input, run_pipeline
from app.verify.schemas import VerifyInput, VerifyResult, ConfidenceBreakdown, SignalResult, PriorScreening

__all__ = [
    "verify_screening",
    "build_verify_input",
    "run_pipeline",
    "VerifyInput",
    "VerifyResult",
    "ConfidenceBreakdown",
    "SignalResult",
    "PriorScreening",
]
