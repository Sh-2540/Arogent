import pytest

from app.verify.rules import score_clinical_consistency, GLUCOSE_HARD_MIN, GLUCOSE_HARD_MAX, BMI_HARD_MIN, BMI_HARD_MAX


class TestHardBounds:
    @pytest.mark.parametrize("glucose", [GLUCOSE_HARD_MIN - 1, GLUCOSE_HARD_MAX + 1, 0, 1000])
    def test_glucose_outside_bounds_capped_and_flagged(self, make_input, glucose):
        result = score_clinical_consistency(make_input(blood_glucose_mg_dl=glucose))
        assert result.score == 10.0
        assert any(f.startswith("glucose_out_of_bounds") for f in result.flags)

    @pytest.mark.parametrize("glucose", [GLUCOSE_HARD_MIN, GLUCOSE_HARD_MIN + 1, GLUCOSE_HARD_MAX - 1, GLUCOSE_HARD_MAX])
    def test_glucose_at_or_inside_bounds_not_flagged(self, make_input, glucose):
        result = score_clinical_consistency(make_input(blood_glucose_mg_dl=glucose))
        assert not any(f.startswith("glucose_out_of_bounds") for f in result.flags)

    @pytest.mark.parametrize("bmi", [BMI_HARD_MIN - 0.1, BMI_HARD_MAX + 0.1])
    def test_bmi_outside_bounds_capped_and_flagged(self, make_input, bmi):
        result = score_clinical_consistency(make_input(bmi=bmi))
        assert result.score == 10.0
        assert any(f.startswith("bmi_out_of_bounds") for f in result.flags)

    def test_hard_bound_result_is_always_available(self, make_input):
        # A hard-bound violation still produces a real (if low) score — it's
        # a NEEDS_REVIEW signal at the aggregate level, not an "unavailable" one.
        result = score_clinical_consistency(make_input(blood_glucose_mg_dl=1000))
        assert result.available is True


class TestSoftConsistency:
    def test_high_glucose_no_corroboration_deducted(self, make_input):
        result = score_clinical_consistency(
            make_input(blood_glucose_mg_dl=220, bmi=22, symptoms=[], family_history_diabetes=False)
        )
        assert result.score == 85.0
        assert any(f.startswith("high_glucose_no_corroboration") for f in result.flags)

    def test_high_glucose_with_corroboration_not_deducted(self, make_input):
        result = score_clinical_consistency(
            make_input(blood_glucose_mg_dl=220, bmi=22, symptoms=["fatigue"], family_history_diabetes=False)
        )
        assert result.score == 100.0
        assert "clinical_values_mutually_reinforcing" in result.flags

    def test_severe_symptoms_with_normal_glucose_deducted(self, make_input):
        result = score_clinical_consistency(
            make_input(blood_glucose_mg_dl=100, symptoms=["blurred_vision"])
        )
        assert result.score == 90.0
        assert any(f.startswith("severe_symptoms_normal_glucose") for f in result.flags)

    def test_typical_values_score_perfectly(self, make_input):
        result = score_clinical_consistency(make_input(blood_glucose_mg_dl=105, bmi=23, symptoms=[]))
        assert result.score == 100.0

    def test_empty_symptoms_not_penalized_by_itself(self, make_input):
        result = score_clinical_consistency(make_input(blood_glucose_mg_dl=110, symptoms=[]))
        assert result.score == 100.0
