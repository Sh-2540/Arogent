"""
Orchestrates the full Arogent Verify pipeline:

    VerifyInput assembly (DB context)
        -> rules.score_clinical_consistency
        -> historical.score_historical_consistency
        -> anomaly.score_behaviour_consistency
        -> geographic.score_geographic_consistency
        -> aggregate.compute_confidence_score / determine_status / determine_recommendation
        -> explain.build_explanation
        -> VerifyResult

This is the only module in the package that touches the database — every
signal module is a pure function over a VerifyInput, which keeps them
independently unit-testable with fixture data (see tests/verify/conftest.py).
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.patient import Patient
from app.models.screening import Screening
from app.models.user import User
from app.verify import rules, historical, geographic, anomaly, aggregate, explain
from app.verify.schemas import VerifyInput, VerifyResult, PriorScreening
from app.schemas.screening import ScreeningCreate


def _load_prior_screenings(db: Session, patient_id: int, before: datetime) -> list[PriorScreening]:
    rows = (
        db.query(Screening)
        .filter(Screening.patient_id == patient_id, Screening.screened_at < before)
        .order_by(Screening.screened_at)
        .all()
    )
    return [
        PriorScreening(
            blood_glucose_mg_dl=r.blood_glucose_mg_dl,
            bmi=r.bmi,
            village_at_screening=r.village_at_screening,
            screened_at=r.screened_at,
        )
        for r in rows
    ]


def _load_asha_screenings_today(db: Session, asha_id: int, on_date: datetime) -> list[PriorScreening]:
    day_start = on_date.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = on_date.replace(hour=23, minute=59, second=59, microsecond=999999)
    rows = (
        db.query(Screening)
        .filter(
            Screening.recorded_by_id == asha_id,
            Screening.screened_at >= day_start,
            Screening.screened_at <= day_end,
            Screening.screened_at < on_date,
        )
        .order_by(Screening.screened_at)
        .all()
    )
    return [
        PriorScreening(
            blood_glucose_mg_dl=r.blood_glucose_mg_dl,
            bmi=r.bmi,
            village_at_screening=r.village_at_screening,
            screened_at=r.screened_at,
        )
        for r in rows
    ]


def build_verify_input(db: Session, screening_data: ScreeningCreate, recorded_by_id: int) -> VerifyInput:
    """Assembles a VerifyInput by pulling in whatever DB context the
    consistency signals need. Raises ValueError if the patient or ASHA
    doesn't exist — callers (the API route, in Module 5) turn this into
    a 404."""
    patient = db.get(Patient, screening_data.patient_id)
    if patient is None:
        raise ValueError(f"Patient {screening_data.patient_id} not found")

    asha = db.get(User, recorded_by_id)
    if asha is None:
        raise ValueError(f"User {recorded_by_id} not found")

    # Naive UTC throughout: SQLite strips tzinfo on read-back regardless, so
    # keeping screened_at timezone-aware at creation time only would break
    # subtraction against prior screenings loaded from the DB (which come
    # back naive). Storing everything as naive UTC from the start avoids
    # the mismatch entirely.
    screened_at = datetime.now(timezone.utc).replace(tzinfo=None)

    return VerifyInput(
        patient_id=screening_data.patient_id,
        blood_glucose_mg_dl=screening_data.blood_glucose_mg_dl,
        bmi=screening_data.bmi,
        family_history_diabetes=screening_data.family_history_diabetes,
        physical_activity_level=screening_data.physical_activity_level,
        symptoms=screening_data.symptoms,
        village_at_screening=screening_data.village_at_screening,
        latitude=screening_data.latitude,
        longitude=screening_data.longitude,
        screened_at=screened_at,
        recorded_by_id=recorded_by_id,
        asha_assigned_village=asha.assigned_village or asha_village_fallback(screening_data.village_at_screening),
        patient_previous_screenings=_load_prior_screenings(db, screening_data.patient_id, screened_at),
        asha_screenings_today=_load_asha_screenings_today(db, recorded_by_id, screened_at),
    )


def asha_village_fallback(village: str) -> str:
    """If an ASHA has no assigned_village on file (shouldn't happen in
    practice, but defensive), fall back to treating the screened village
    as the assignment rather than crashing or unfairly penalizing every
    screening this worker ever logs."""
    return village


def run_pipeline(data: VerifyInput) -> VerifyResult:
    """Pure function: given a fully-assembled VerifyInput, runs all four
    signals and returns a VerifyResult. No DB access — fully unit-testable."""
    clinical = rules.score_clinical_consistency(data)
    hist = historical.score_historical_consistency(data)
    behaviour = anomaly.score_behaviour_consistency(data)
    geo = geographic.score_geographic_consistency(data)

    confidence_score, breakdown = aggregate.compute_confidence_score(clinical, hist, behaviour, geo)

    hard_bound_violation = any(f.startswith(("glucose_out_of_bounds", "bmi_out_of_bounds")) for f in clinical.flags)
    status = aggregate.determine_status(confidence_score, hard_bound_violation)
    recommendation = aggregate.determine_recommendation(status)

    explanation = explain.build_explanation(clinical, hist, behaviour, geo)

    return VerifyResult(
        confidence_score=confidence_score,
        status=status,
        signals=breakdown,
        recommendation=recommendation,
        explanation=explanation,
        hard_bound_violation=hard_bound_violation,
    )


def verify_screening(db: Session, screening_data: ScreeningCreate, recorded_by_id: int) -> tuple[Screening, VerifyResult]:
    """
    Public entrypoint for the package. Assembles context, runs the pipeline,
    persists a new Screening row with the Arogent Verify output written onto
    it, and returns both the ORM row and the VerifyResult (the row is what
    Module 5's API route commits; the VerifyResult is what it serializes
    back to the client via schemas.screening.ScreeningResult).

    Diabetes risk prediction (Arogent Risk, Module 4) is deliberately NOT
    called from here — the API route decides whether to call it, based on
    result.status, keeping Verify and Risk as independently testable
    packages that don't import each other.
    """
    verify_input = build_verify_input(db, screening_data, recorded_by_id)
    result = run_pipeline(verify_input)

    screening = Screening(
        patient_id=screening_data.patient_id,
        recorded_by_id=recorded_by_id,
        blood_glucose_mg_dl=screening_data.blood_glucose_mg_dl,
        bmi=screening_data.bmi,
        family_history_diabetes=screening_data.family_history_diabetes,
        physical_activity_level=screening_data.physical_activity_level,
        symptoms=screening_data.symptoms,
        village_at_screening=screening_data.village_at_screening,
        latitude=screening_data.latitude,
        longitude=screening_data.longitude,
        screened_at=verify_input.screened_at,
        clinical_consistency_score=result.signals.clinical_consistency_score,
        historical_consistency_score=result.signals.historical_consistency_score,
        behaviour_consistency_score=result.signals.behaviour_consistency_score,
        geographic_consistency_score=result.signals.geographic_consistency_score,
        confidence_score=result.confidence_score,
        confidence_status=result.status,
        confidence_reasons=result.explanation,
    )
    db.add(screening)
    db.commit()
    db.refresh(screening)

    return screening, result
