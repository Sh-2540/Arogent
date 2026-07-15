"""Shared fixtures for the Arogent Verify test suite."""
from datetime import datetime, timezone

import pytest

from app.verify.schemas import VerifyInput, PriorScreening


def make_verify_input(**overrides) -> VerifyInput:
    """Builds a VerifyInput with sensible clinically-plausible defaults;
    tests override only the fields relevant to what they're checking."""
    defaults = dict(
        patient_id=1,
        blood_glucose_mg_dl=110.0,
        bmi=24.0,
        family_history_diabetes=False,
        physical_activity_level="MODERATE",
        symptoms=[],
        village_at_screening="Wadgaon",
        latitude=None,
        longitude=None,
        screened_at=datetime(2026, 3, 10, 11, 0, tzinfo=timezone.utc),  # a Tuesday, 11am
        recorded_by_id=1,
        asha_assigned_village="Wadgaon",
        patient_previous_screenings=[],
        asha_screenings_today=[],
    )
    defaults.update(overrides)
    return VerifyInput(**defaults)


@pytest.fixture
def base_input() -> VerifyInput:
    return make_verify_input()


@pytest.fixture
def make_input():
    """Factory fixture so tests can build custom inputs inline."""
    return make_verify_input


@pytest.fixture
def make_prior():
    def _make(**overrides) -> PriorScreening:
        defaults = dict(
            blood_glucose_mg_dl=100.0,
            bmi=23.0,
            village_at_screening="Wadgaon",
            screened_at=datetime(2026, 3, 1, 10, 0, tzinfo=timezone.utc),
        )
        defaults.update(overrides)
        return PriorScreening(**defaults)
    return _make
