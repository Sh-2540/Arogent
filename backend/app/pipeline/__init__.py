"""
Pipeline Orchestrator — composes Arogent Verify, Arogent Risk, and the
Referral Engine into one screening flow. See service.py's docstring for
the full architecture diagram and why this separation matters.
"""
from app.pipeline.service import (
    run_screening_pipeline,
    get_screening,
    get_screening_result,
    get_patient_screening_history,
)

__all__ = [
    "run_screening_pipeline",
    "get_screening",
    "get_screening_result",
    "get_patient_screening_history",
]
