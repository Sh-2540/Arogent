from app.core.enums import RiskLevel
from app.risk.service import determine_risk_level, RISK_LOW_MAX, RISK_HIGH_MIN
from app.risk import predict_diabetes_risk, RiskInput
from app.core.enums import ConfidenceStatus


class TestRiskLevelThresholds:
    def test_at_or_below_low_max_is_low(self):
        assert determine_risk_level(RISK_LOW_MAX) == RiskLevel.LOW
        assert determine_risk_level(0.0) == RiskLevel.LOW

    def test_at_or_above_high_min_is_high(self):
        assert determine_risk_level(RISK_HIGH_MIN) == RiskLevel.HIGH
        assert determine_risk_level(100.0) == RiskLevel.HIGH

    def test_between_thresholds_is_moderate(self):
        assert determine_risk_level((RISK_LOW_MAX + RISK_HIGH_MIN) / 2) == RiskLevel.MODERATE


class TestFeatureContributions:
    def test_returns_at_most_five_contributions(self):
        data = RiskInput(age=60, bmi=30, blood_glucose_mg_dl=220, family_history_diabetes=True,
                          physical_activity_level="LOW", symptoms=["fatigue", "frequent_urination"])
        result = predict_diabetes_risk(data, ConfidenceStatus.HIGH)
        assert len(result.top_contributing_features) <= 5

    def test_contributions_sorted_by_absolute_magnitude_descending(self):
        data = RiskInput(age=60, bmi=30, blood_glucose_mg_dl=220, family_history_diabetes=True,
                          physical_activity_level="LOW", symptoms=["fatigue"])
        result = predict_diabetes_risk(data, ConfidenceStatus.HIGH)
        magnitudes = [abs(c.contribution) for c in result.top_contributing_features]
        assert magnitudes == sorted(magnitudes, reverse=True)

    def test_higher_risk_inputs_score_higher_than_lower_risk_inputs(self):
        """Sanity check on model direction, not an exact value — a patient
        with every major risk factor present should score meaningfully
        higher than one with none of them."""
        high_risk_input = RiskInput(
            age=70, bmi=34, blood_glucose_mg_dl=240, family_history_diabetes=True,
            physical_activity_level="LOW", symptoms=["fatigue", "frequent_urination", "excessive_thirst"],
        )
        low_risk_input = RiskInput(
            age=25, bmi=21, blood_glucose_mg_dl=90, family_history_diabetes=False,
            physical_activity_level="HIGH", symptoms=[],
        )
        high_result = predict_diabetes_risk(high_risk_input, ConfidenceStatus.HIGH)
        low_result = predict_diabetes_risk(low_risk_input, ConfidenceStatus.HIGH)
        assert high_result.risk_score > low_result.risk_score
