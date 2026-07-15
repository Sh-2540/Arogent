"""
Arogent Risk service.

CRITICAL ARCHITECTURE RULE (enforced here, not just documented): Arogent
Risk must NEVER run on a screening that Arogent Verify didn't mark HIGH
confidence. This is checked inside predict_diabetes_risk itself — it
raises PermissionError if called with any other status — precisely so
this rule can't be silently bypassed by a future caller (e.g. a rushed
API route in a later module) that forgets to check first. The gate lives
in the one place that can't be skipped, not in caller discipline.

    Arogent Verify
         │
    Confidence == HIGH?
         │
    Yes ─────────► Arogent Risk (this module)
         │
    No
    ▼
    Repeat Screening / Escalate for PHC Review  (Arogent Risk is never called)
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.enums import ConfidenceStatus, RiskLevel, ReferralStatus
from app.models.patient import Patient
from app.models.screening import Screening
from app.risk import model as risk_model
from app.risk.features import (
    build_feature_vector,
    compute_logistic_regression_contributions,
    compute_global_importance_contributions,
)
from app.risk.schemas import RiskInput, RiskResult

RISK_LOW_MAX = 30.0
RISK_HIGH_MIN = 70.0


class ConfidenceGateError(PermissionError):
    """Raised when Arogent Risk is called on a screening that didn't reach
    HIGH confidence. This is a programming error in the caller, not a normal
    business-logic outcome — it should never happen if Module 5's API
    routes are wired correctly, but this module doesn't trust that."""
    pass


def determine_risk_level(risk_score: float) -> RiskLevel:
    if risk_score >= RISK_HIGH_MIN:
        return RiskLevel.HIGH
    if risk_score <= RISK_LOW_MAX:
        return RiskLevel.LOW
    return RiskLevel.MODERATE


def predict_diabetes_risk(risk_input: RiskInput, confidence_status: ConfidenceStatus) -> RiskResult:
    """
    Pure-ish function (no DB access) that runs the model and returns a
    RiskResult — but ONLY if confidence_status is HIGH. This is the
    architectural gate described in this module's docstring.
    """
    if confidence_status != ConfidenceStatus.HIGH:
        raise ConfidenceGateError(
            f"Arogent Risk cannot run on a screening with confidence_status="
            f"{confidence_status!r}. Only HIGH-confidence screenings may "
            f"reach the risk model — see this module's docstring."
        )

    feature_vector = build_feature_vector(risk_input)
    probability = risk_model.predict_probability(feature_vector)
    risk_score = round(probability * 100, 1)
    risk_level = determine_risk_level(risk_score)

    if risk_model.is_logistic_regression():
        model, scaler = risk_model.get_model_and_scaler()
        contributions = compute_logistic_regression_contributions(model, scaler, feature_vector)
    else:
        contributions = compute_global_importance_contributions(risk_model.get_feature_importance())

    metadata = risk_model.get_metadata()

    return RiskResult(
        risk_score=risk_score,
        risk_level=risk_level,
        model_used=metadata["model_used"],
        top_contributing_features=contributions,
    )


def run_risk_prediction_for_screening(db: Session, screening: Screening) -> RiskResult | None:
    """
    Public entrypoint that Module 5's API route calls after Arogent Verify.
    Returns None (does NOT call predict_diabetes_risk) if the screening's
    confidence_status isn't HIGH — this is the second layer of the gate,
    at the DB-aware boundary, so a caller only has to check the return
    value rather than pre-filter before calling.

    On a HIGH-risk result, also generates an explicit Referral record via
    the Referral Engine (app.referral) — not just a status flag — so the
    Result screen has something tangible (a PHC name, priority, and reason)
    to display, not only a risk number.
    """
    if screening.confidence_status != ConfidenceStatus.HIGH:
        return None

    patient = db.get(Patient, screening.patient_id)
    if patient is None:
        raise ValueError(f"Patient {screening.patient_id} not found")

    risk_input = RiskInput(
        age=patient.age,
        bmi=screening.bmi,
        blood_glucose_mg_dl=screening.blood_glucose_mg_dl,
        family_history_diabetes=screening.family_history_diabetes,
        physical_activity_level=screening.physical_activity_level,
        symptoms=screening.symptoms,
    )

    result = predict_diabetes_risk(risk_input, screening.confidence_status)

    screening.risk_score = result.risk_score
    screening.risk_level = result.risk_level

    if result.risk_level == RiskLevel.HIGH:
        # Import kept local to avoid a module-level circular import between
        # app.risk and app.referral (referral imports RiskResult from risk.schemas).
        from app.referral import generate_referral

        generate_referral(db, patient, screening, result)
        screening.referral_status = ReferralStatus.PENDING

    return result
