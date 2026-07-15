"""
Referral Engine — generates an explicit, tangible Referral record whenever
Arogent Risk produces a HIGH risk_level. Kept as its own small package
(rather than folded into app/risk) so the architecture stays cleanly
separated: Verify decides confidence, Risk decides diabetes risk, Referral
decides what happens next for the patient. None of these import each
other's internals — they're composed by the service layer in the API
routes (Module 5).
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.patient import Patient
from app.models.screening import Screening
from app.models.referral import Referral
from app.core.enums import ReferralStatus
from app.risk.schemas import RiskResult


def build_referral_reason(risk_result: RiskResult) -> str:
    """A short, human-readable reason referencing the top contributing
    factors — this is what a PHC officer sees, not just a bare score."""
    top_factors = [c.display_name for c in risk_result.top_contributing_features[:2]]
    factors_text = " and ".join(top_factors) if top_factors else "multiple risk factors"
    return (
        f"Diabetes risk score {risk_result.risk_score}% (HIGH) — "
        f"primary contributing factors: {factors_text}."
    )


def generate_referral(
    db: Session, patient: Patient, screening: Screening, risk_result: RiskResult
) -> Referral:
    """
    Creates and adds (but does not commit — the caller's transaction owns
    that) a Referral row. Only ever called when risk_result.risk_level is
    HIGH; the caller (app.risk.service.run_risk_prediction_for_screening)
    is responsible for that check, matching this package's job being
    referral *generation*, not risk gating.
    """
    referral = Referral(
        patient_id=patient.id,
        screening_id=screening.id,
        phc=f"Ayushman Arogya Mandir, {screening.village_at_screening}",
        priority=risk_result.risk_level.value,
        reason=build_referral_reason(risk_result),
        status=ReferralStatus.PENDING,
    )
    db.add(referral)
    return referral
