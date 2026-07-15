"""
Integration test: full Arogent Verify pipeline, from a ScreeningCreate
payload through to a persisted Screening row, against an in-memory SQLite
DB seeded with a patient + prior screening history.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import User, Patient
from app.core.enums import UserRole, ConfidenceStatus
from app.schemas.screening import ScreeningCreate
from app.verify.service import verify_screening


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def seeded_asha(db_session):
    asha = User(full_name="Sunita Patil", username="sunita_asha", hashed_password="x",
                role=UserRole.ASHA, assigned_village="Wadgaon")
    db_session.add(asha)
    db_session.commit()
    db_session.refresh(asha)
    return asha


@pytest.fixture
def seeded_patient(db_session, seeded_asha):
    patient = Patient(full_name="Ramesh Kale", age=52, gender="Male", village="Wadgaon",
                       registered_by_id=seeded_asha.id)
    db_session.add(patient)
    db_session.commit()
    db_session.refresh(patient)
    return patient


class TestVerifyScreeningEndToEnd:
    def test_high_confidence_screening_persists_all_fields(self, db_session, seeded_asha, seeded_patient):
        screening_data = ScreeningCreate(
            patient_id=seeded_patient.id,
            blood_glucose_mg_dl=115.0,
            bmi=23.0,
            family_history_diabetes=False,
            physical_activity_level="MODERATE",
            symptoms=[],
            village_at_screening="Wadgaon",
        )
        screening, result = verify_screening(db_session, screening_data, seeded_asha.id)

        assert screening.id is not None
        assert screening.confidence_score == result.confidence_score
        assert screening.confidence_status == result.status
        assert screening.confidence_reasons == result.explanation
        assert len(result.explanation) == 4

    def test_second_screening_uses_first_as_history(self, db_session, seeded_asha, seeded_patient):
        first_data = ScreeningCreate(
            patient_id=seeded_patient.id, blood_glucose_mg_dl=100.0, bmi=23.0,
            family_history_diabetes=False, physical_activity_level="MODERATE",
            symptoms=[], village_at_screening="Wadgaon",
        )
        _, first_result = verify_screening(db_session, first_data, seeded_asha.id)
        assert first_result.signals.historical_consistency_score == 0.0  # unavailable, displayed as 0
        assert any("first recorded screening" in e for e in first_result.explanation)

        second_data = ScreeningCreate(
            patient_id=seeded_patient.id, blood_glucose_mg_dl=105.0, bmi=23.2,
            family_history_diabetes=False, physical_activity_level="MODERATE",
            symptoms=[], village_at_screening="Wadgaon",
        )
        _, second_result = verify_screening(db_session, second_data, seeded_asha.id)
        # Now that a prior screening exists, historical consistency should be
        # available and scored well (values are close together).
        assert second_result.signals.historical_consistency_score > 0.0

    def test_raises_for_unknown_patient(self, db_session, seeded_asha):
        bad_data = ScreeningCreate(
            patient_id=99999, blood_glucose_mg_dl=110.0, bmi=23.0,
            family_history_diabetes=False, physical_activity_level="MODERATE",
            symptoms=[], village_at_screening="Wadgaon",
        )
        with pytest.raises(ValueError, match="Patient 99999 not found"):
            verify_screening(db_session, bad_data, seeded_asha.id)

    def test_hard_bound_violation_persists_needs_review(self, db_session, seeded_asha, seeded_patient):
        bad_data = ScreeningCreate(
            patient_id=seeded_patient.id, blood_glucose_mg_dl=800.0, bmi=23.0,
            family_history_diabetes=False, physical_activity_level="MODERATE",
            symptoms=[], village_at_screening="Wadgaon",
        )
        screening, result = verify_screening(db_session, bad_data, seeded_asha.id)
        assert screening.confidence_status == ConfidenceStatus.NEEDS_REVIEW
        assert result.recommendation == "Escalate for PHC Review"
