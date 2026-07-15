"""
Tests for the confidence gate — the single most important architectural
rule in Arogent Risk: it must never run on anything but HIGH confidence.
"""
import pytest

from app.core.enums import ConfidenceStatus
from app.risk import predict_diabetes_risk, RiskInput, ConfidenceGateError


def _make_input(**overrides) -> RiskInput:
    defaults = dict(
        age=55, bmi=27.0, blood_glucose_mg_dl=150.0,
        family_history_diabetes=False, physical_activity_level="MODERATE", symptoms=[],
    )
    defaults.update(overrides)
    return RiskInput(**defaults)


class TestConfidenceGate:
    def test_high_confidence_succeeds(self):
        result = predict_diabetes_risk(_make_input(), ConfidenceStatus.HIGH)
        assert 0.0 <= result.risk_score <= 100.0

    @pytest.mark.parametrize("status", [
        ConfidenceStatus.MEDIUM,
        ConfidenceStatus.LOW,
        ConfidenceStatus.NEEDS_REVIEW,
    ])
    def test_non_high_confidence_always_raises(self, status):
        with pytest.raises(ConfidenceGateError):
            predict_diabetes_risk(_make_input(), status)

    def test_gate_error_message_names_the_offending_status(self):
        with pytest.raises(ConfidenceGateError, match="MEDIUM"):
            predict_diabetes_risk(_make_input(), ConfidenceStatus.MEDIUM)
