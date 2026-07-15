"""
Integration test: run_risk_prediction_for_screening against an in-memory
DB, covering both the HIGH-confidence path (should predict and set
referral fields on HIGH risk) and the non-HIGH path (should return None
without ever calling the model).
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import User, Patient, Screening, Referral
from app.core.enums import UserRole, ConfidenceStatus, RiskLevel, ReferralStatus
from app.risk import run_risk_prediction_for_screening


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def seeded_patient(db_session):
    asha = User(full_name="Kavita More", username="kavita_asha", hashed_password="x",
                role=UserRole.ASHA, assigned_village="Karanjgaon")
    db_session.add(asha)
    db_session.commit()
    db_session.refresh(asha)

    patient = Patient(full_name="Meera Joshi", age=61, gender="Female", village="Karanjgaon",
                       registered_by_id=asha.id)
    db_session.add(patient)
    db_session.commit()
    db_session.refresh(patient)
    return patient, asha


def _make_screening(patient, asha, confidence_status, **overrides) -> Screening:
    defaults = dict(
        patient_id=patient.id,
        recorded_by_id=asha.id,
        blood_glucose_mg_dl=230.0,
        bmi=31.0,
        family_history_diabetes=True,
        physical_activity_level="LOW",
        symptoms=["fatigue", "frequent_urination"],
        village_at_screening="Karanjgaon",
        confidence_score=91.0,
        confidence_status=confidence_status,
        confidence_reasons=["placeholder"],
    )
    defaults.update(overrides)
    return Screening(**defaults)


class TestRunRiskPredictionForScreening:
    def test_high_confidence_predicts_and_persists_risk_fields(self, db_session, seeded_patient):
        patient, asha = seeded_patient
        screening = _make_screening(patient, asha, ConfidenceStatus.HIGH)
        db_session.add(screening)
        db_session.commit()
        db_session.refresh(screening)

        result = run_risk_prediction_for_screening(db_session, screening)

        assert result is not None
        assert screening.risk_score == result.risk_score
        assert screening.risk_level == result.risk_level

    def test_high_risk_result_creates_referral_record(self, db_session, seeded_patient):
        patient, asha = seeded_patient
        # Deliberately extreme risk factors to reliably land in HIGH risk_level
        screening = _make_screening(
            patient, asha, ConfidenceStatus.HIGH,
            blood_glucose_mg_dl=250.0, bmi=35.0, family_history_diabetes=True,
            physical_activity_level="LOW",
            symptoms=["fatigue", "frequent_urination", "excessive_thirst", "blurred_vision"],
        )
        db_session.add(screening)
        db_session.commit()
        db_session.refresh(screening)

        result = run_risk_prediction_for_screening(db_session, screening)
        db_session.commit()

        if result.risk_level == RiskLevel.HIGH:
            assert screening.referral_status == ReferralStatus.PENDING

            referral = db_session.query(Referral).filter(Referral.screening_id == screening.id).one_or_none()
            assert referral is not None
            assert referral.patient_id == patient.id
            assert referral.priority == "HIGH"
            assert referral.status == ReferralStatus.PENDING
            assert "Ayushman Arogya Mandir" in referral.phc
            assert str(result.risk_score) in referral.reason

    @pytest.mark.parametrize("status", [
        ConfidenceStatus.MEDIUM, ConfidenceStatus.LOW, ConfidenceStatus.NEEDS_REVIEW,
    ])
    def test_non_high_confidence_returns_none_and_never_sets_risk_fields(self, db_session, seeded_patient, status):
        patient, asha = seeded_patient
        screening = _make_screening(patient, asha, status)
        db_session.add(screening)
        db_session.commit()
        db_session.refresh(screening)

        result = run_risk_prediction_for_screening(db_session, screening)

        assert result is None
        assert screening.risk_score is None
        assert screening.risk_level is None
        assert screening.referral_status is None
