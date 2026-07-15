"""
Pipeline Orchestrator — the single place that composes Arogent Verify,
Arogent Risk, and the Referral Engine into one screening submission flow.

    Frontend
        │
        ▼
    Pipeline Orchestrator (this module)
        │
        ├──────────► Arogent Verify   (app.verify — independent package)
        │                 │
        │            confidence == HIGH?
        │                 │
        │            Yes ─┴─► Arogent Risk   (app.risk — independent package)
        │                          │
        │                     risk_level == HIGH?
        │                          │
        │                     Yes ─┴─► Referral Engine (app.referral)
        │
        └──────────► (No — screening stays at its Verify-only state;
                       Arogent Risk is never called. This is the
                       confidence gate, enforced here AND, redundantly,
                       inside app.risk.service itself — see that
                       module's ConfidenceGateError.)

Arogent Verify and Arogent Risk do not import each other. Neither knows
the other exists. This module is the ONLY place they're composed — which
is what makes each independently testable (see tests/verify/ and
tests/risk/, neither of which imports this module) and what makes the
"Risk never runs on low-confidence data" claim a structural fact about
the codebase, not just a convention someone has to remember to follow.

No scoring, thresholds, or gating logic lives in the API route (Module 5)
that calls run_screening_pipeline — all of that is here or in the Verify/
Risk/Referral packages themselves.
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.enums import ConfidenceStatus, RiskLevel
from app.models.screening import Screening
from app.schemas.screening import ScreeningCreate, ScreeningResult, ConfidenceBreakdown
from app.verify import verify_screening
from app.verify.aggregate import determine_recommendation
from app.risk import run_risk_prediction_for_screening

# Final-state recommendation once Risk has actually run — replaces the
# Verify-stage "Proceed to Risk Prediction" message, which is only ever a
# mid-pipeline placeholder, not something that should reach the response.
_RISK_LEVEL_RECOMMENDATIONS = {
    RiskLevel.HIGH: "Referral generated — refer to PHC for confirmation and treatment.",
    RiskLevel.MODERATE: "Schedule a follow-up visit to Ayushman Arogya Mandir within one month.",
    RiskLevel.LOW: "Provide lifestyle advice and schedule the next routine screening.",
}


def run_screening_pipeline(db: Session, screening_data: ScreeningCreate, recorded_by_id: int) -> ScreeningResult:
    """
    Runs a screening through the full pipeline: Verify, then — only if
    confidence is HIGH — Risk and (only if risk is HIGH) Referral. Returns
    the final response shape via get_screening_result, so POST and GET
    can never drift apart.
    """
    screening, _ = verify_screening(db, screening_data, recorded_by_id)

    if screening.confidence_status == ConfidenceStatus.HIGH:
        run_risk_prediction_for_screening(db, screening)

    db.commit()
    db.refresh(screening)

    result = get_screening_result(db, screening.id)
    assert result is not None  # just created it — this should be unreachable
    return result


def get_screening(db: Session, screening_id: int) -> Screening | None:
    return db.get(Screening, screening_id)


def get_screening_result(db: Session, screening_id: int) -> ScreeningResult | None:
    """Builds a ScreeningResult for an already-persisted screening. This is
    the ONLY place that assembles the response shape — both the POST and
    GET screening routes go through here, so response-building logic
    never needs to be duplicated or kept in sync across call sites."""
    screening = get_screening(db, screening_id)
    if screening is None:
        return None

    if screening.confidence_status == ConfidenceStatus.HIGH and screening.risk_level is not None:
        recommendation = _RISK_LEVEL_RECOMMENDATIONS[screening.risk_level]
    else:
        recommendation = determine_recommendation(screening.confidence_status)

    return ScreeningResult(
        id=screening.id,
        patient_id=screening.patient_id,
        screened_at=screening.screened_at,
        blood_glucose_mg_dl=screening.blood_glucose_mg_dl,
        bmi=screening.bmi,
        confidence_score=screening.confidence_score,
        confidence_status=screening.confidence_status,
        confidence_breakdown=ConfidenceBreakdown(
            clinical_consistency_score=screening.clinical_consistency_score,
            historical_consistency_score=screening.historical_consistency_score,
            behaviour_consistency_score=screening.behaviour_consistency_score,
            geographic_consistency_score=screening.geographic_consistency_score,
        ),
        confidence_reasons=screening.confidence_reasons,
        risk_score=screening.risk_score,
        risk_level=screening.risk_level,
        referral_status=screening.referral_status,
        recommendation=recommendation,
    )


def get_patient_screening_history(db: Session, patient_id: int, limit: int = 20) -> list[Screening]:
    return (
        db.query(Screening)
        .filter(Screening.patient_id == patient_id)
        .order_by(Screening.screened_at.desc())
        .limit(limit)
        .all()
    )
