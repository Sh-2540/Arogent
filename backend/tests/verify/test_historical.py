from datetime import datetime, timezone

from app.verify.historical import score_historical_consistency


class TestNoHistory:
    def test_first_screening_is_unavailable_not_penalized(self, make_input):
        result = score_historical_consistency(make_input(patient_previous_screenings=[]))
        assert result.available is False
        assert "no_prior_history" in result.flags


class TestConsistentHistory:
    def test_similar_reading_scores_perfectly(self, make_input, make_prior):
        prior = make_prior(
            blood_glucose_mg_dl=108.0, bmi=23.5,
            screened_at=datetime(2026, 3, 1, 10, 0, tzinfo=timezone.utc),
        )
        result = score_historical_consistency(
            make_input(
                blood_glucose_mg_dl=110.0, bmi=24.0,
                screened_at=datetime(2026, 3, 10, 11, 0, tzinfo=timezone.utc),
                patient_previous_screenings=[prior],
            )
        )
        assert result.available is True
        assert result.score == 100.0
        assert "consistent_with_screening_history" in result.flags


class TestImplausibleSwing:
    def test_large_glucose_jump_recent_deducted(self, make_input, make_prior):
        prior = make_prior(
            blood_glucose_mg_dl=95.0,
            screened_at=datetime(2026, 3, 9, 10, 0, tzinfo=timezone.utc),  # 1 day ago
        )
        result = score_historical_consistency(
            make_input(
                blood_glucose_mg_dl=280.0,  # 185 delta > 150 threshold
                screened_at=datetime(2026, 3, 10, 11, 0, tzinfo=timezone.utc),
                patient_previous_screenings=[prior],
            )
        )
        assert result.score < 100.0
        assert any(f.startswith("implausible_glucose_swing") for f in result.flags)

    def test_same_size_jump_scores_higher_when_older(self, make_input, make_prior):
        """A given swing against an older reading should be penalized less
        than the same swing against a very recent one (recency weighting)."""
        recent_prior = make_prior(
            blood_glucose_mg_dl=95.0,
            screened_at=datetime(2026, 3, 9, 10, 0, tzinfo=timezone.utc),  # 1 day ago
        )
        older_prior = make_prior(
            blood_glucose_mg_dl=95.0,
            screened_at=datetime(2026, 2, 25, 10, 0, tzinfo=timezone.utc),  # 13 days ago
        )
        recent_result = score_historical_consistency(
            make_input(blood_glucose_mg_dl=280.0,
                       screened_at=datetime(2026, 3, 10, 11, 0, tzinfo=timezone.utc),
                       patient_previous_screenings=[recent_prior])
        )
        older_result = score_historical_consistency(
            make_input(blood_glucose_mg_dl=280.0,
                       screened_at=datetime(2026, 3, 10, 11, 0, tzinfo=timezone.utc),
                       patient_previous_screenings=[older_prior])
        )
        assert older_result.score > recent_result.score

    def test_swing_beyond_short_window_not_penalized(self, make_input, make_prior):
        prior = make_prior(
            blood_glucose_mg_dl=95.0,
            screened_at=datetime(2025, 12, 1, 10, 0, tzinfo=timezone.utc),  # >14 days ago
        )
        result = score_historical_consistency(
            make_input(blood_glucose_mg_dl=280.0,
                       screened_at=datetime(2026, 3, 10, 11, 0, tzinfo=timezone.utc),
                       patient_previous_screenings=[prior])
        )
        assert not any(f.startswith("implausible_glucose_swing") for f in result.flags)


class TestDuplicateScreening:
    def test_screening_within_a_few_hours_flagged_as_possible_duplicate(self, make_input, make_prior):
        prior = make_prior(
            blood_glucose_mg_dl=110.0,
            screened_at=datetime(2026, 3, 10, 9, 0, tzinfo=timezone.utc),  # 2 hours before
        )
        result = score_historical_consistency(
            make_input(blood_glucose_mg_dl=112.0,
                       screened_at=datetime(2026, 3, 10, 11, 0, tzinfo=timezone.utc),
                       patient_previous_screenings=[prior])
        )
        assert any(f.startswith("possible_duplicate_screening") for f in result.flags)
        assert result.score < 100.0

    def test_screening_a_full_day_later_not_flagged_as_duplicate(self, make_input, make_prior):
        prior = make_prior(
            blood_glucose_mg_dl=110.0,
            screened_at=datetime(2026, 3, 9, 11, 0, tzinfo=timezone.utc),
        )
        result = score_historical_consistency(
            make_input(blood_glucose_mg_dl=112.0,
                       screened_at=datetime(2026, 3, 10, 11, 0, tzinfo=timezone.utc),
                       patient_previous_screenings=[prior])
        )
        assert not any(f.startswith("possible_duplicate_screening") for f in result.flags)
