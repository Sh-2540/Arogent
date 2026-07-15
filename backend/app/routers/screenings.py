"""Screening routes — the core Arogent pipeline endpoint. All orchestration
and response-building logic lives in app.pipeline (the Pipeline
Orchestrator); this file only translates HTTP <-> service calls, matching
the thin-routes architecture — no scoring, thresholds, or gating logic here."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.enums import UserRole
from app.core.security import get_current_user, require_roles
from app.models.user import User
from app.schemas.screening import ScreeningCreate, ScreeningResult, ScreeningSummary
from app.pipeline import run_screening_pipeline, get_screening_result, get_patient_screening_history

router = APIRouter(prefix="/screenings", tags=["screenings"])


@router.post(
    "",
    response_model=ScreeningResult,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a diabetes screening",
    description=(
        "Runs the full Arogent pipeline: Arogent Verify estimates a Screening "
        "Confidence Score first. Arogent Risk only runs — and a referral is "
        "only generated — if confidence is HIGH; otherwise the response "
        "recommends repeating the screening or escalating for PHC review. "
        "This gating is enforced in the service layer, not just documented."
    ),
    dependencies=[Depends(require_roles(UserRole.ASHA))],
    responses={404: {"description": "Patient not found"}},
)
def submit_screening(
    data: ScreeningCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ScreeningResult:
    try:
        return run_screening_pipeline(db, data, recorded_by_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.get(
    "/{screening_id}",
    response_model=ScreeningResult,
    summary="Get a screening result by ID",
    description="Retrieves a previously submitted screening's full result — confidence breakdown, risk score, and referral status, if any.",
    responses={404: {"description": "Screening not found"}},
)
def read_screening(screening_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> ScreeningResult:
    result = get_screening_result(db, screening_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Screening {screening_id} not found")
    return result


@router.get(
    "/patient/{patient_id}",
    response_model=list[ScreeningSummary],
    summary="Get a patient's screening history",
    description="Lists a patient's past screenings, most recent first — used by the ASHA app to show prior visits.",
)
def read_patient_history(patient_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> list[ScreeningSummary]:
    screenings = get_patient_screening_history(db, patient_id)
    return [ScreeningSummary.model_validate(s) for s in screenings]
