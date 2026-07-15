"""Patient routes — registration and lookup. Business logic lives in
app.services.patient_service."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.enums import UserRole
from app.core.security import get_current_user, require_roles
from app.models.user import User
from app.schemas.patient import PatientCreate, PatientRead, PatientSummary
from app.services.patient_service import register_patient, get_patient, search_patients

router = APIRouter(prefix="/patients", tags=["patients"])


@router.post(
    "",
    response_model=PatientRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new patient",
    description="Registers a patient in the ASHA worker's village. Only ASHA workers may register patients.",
    dependencies=[Depends(require_roles(UserRole.ASHA))],
)
def create_patient(
    data: PatientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PatientRead:
    patient = register_patient(db, data, registered_by_id=current_user.id)
    return PatientRead.model_validate(patient)


@router.get(
    "/{patient_id}",
    response_model=PatientRead,
    summary="Get a patient by ID",
    description="Retrieves a single patient's demographic record by ID.",
    responses={404: {"description": "Patient not found"}},
)
def read_patient(patient_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> PatientRead:
    patient = get_patient(db, patient_id)
    if patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Patient {patient_id} not found")
    return PatientRead.model_validate(patient)


@router.get(
    "",
    response_model=list[PatientSummary],
    summary="Search patients",
    description="Search patients by village and/or name, for the ASHA worker's registration/screening flow.",
)
def list_patients(
    village: str | None = None,
    name: str | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[PatientSummary]:
    patients = search_patients(db, village=village, name=name)
    return [PatientSummary.model_validate(p) for p in patients]
