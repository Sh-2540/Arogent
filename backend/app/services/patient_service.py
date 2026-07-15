"""Patient service — registration and lookup, kept out of the router."""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.patient import Patient
from app.schemas.patient import PatientCreate


def register_patient(db: Session, data: PatientCreate, registered_by_id: int) -> Patient:
    patient = Patient(
        full_name=data.full_name,
        age=data.age,
        gender=data.gender,
        village=data.village,
        phone_number=data.phone_number,
        date_of_birth=data.date_of_birth,
        registered_by_id=registered_by_id,
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


def get_patient(db: Session, patient_id: int) -> Patient | None:
    return db.get(Patient, patient_id)


def search_patients(db: Session, village: str | None = None, name: str | None = None, limit: int = 20) -> list[Patient]:
    query = db.query(Patient)
    if village:
        query = query.filter(Patient.village == village)
    if name:
        query = query.filter(Patient.full_name.ilike(f"%{name}%"))
    return query.order_by(Patient.registered_at.desc()).limit(limit).all()
