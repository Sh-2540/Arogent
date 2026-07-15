from datetime import datetime, timezone

from app.verify.anomaly import score_behaviour_consistency


class TestFirstScreeningOfDay:
    def test_no_prior_screenings_today_does_not_crash_or_penalize_pace(self, make_input):
        result = score_behaviour_consistency(make_input(asha_screenings_today=[]))
        assert result.available is True
        assert not any(f.startswith("rapid_screening_pace") for f in result.flags)


class TestRapidFirePace:
    def test_screening_seconds_after_previous_flagged(self, make_input, make_prior):
        prior = make_prior(screened_at=datetime(2026, 3, 10, 10, 58, tzinfo=timezone.utc))
        result = score_behaviour_consistency(
            make_input(
                screened_at=datetime(2026, 3, 10, 11, 0, tzinfo=timezone.utc),  # 2 min later
                asha_screenings_today=[prior],
            )
        )
        assert any(f.startswith("rapid_screening_pace") for f in result.flags)
        assert result.score < 100.0

    def test_normal_gap_not_flagged(self, make_input, make_prior):
        prior = make_prior(screened_at=datetime(2026, 3, 10, 10, 30, tzinfo=timezone.utc))
        result = score_behaviour_consistency(
            make_input(
                screened_at=datetime(2026, 3, 10, 11, 0, tzinfo=timezone.utc),  # 30 min later
                asha_screenings_today=[prior],
            )
        )
        assert not any(f.startswith("rapid_screening_pace") for f in result.flags)


class TestWorkingHours:
    def test_screening_at_2am_flagged(self, make_input):
        result = score_behaviour_consistency(
            make_input(screened_at=datetime(2026, 3, 10, 2, 0, tzinfo=timezone.utc))
        )
        assert any(f.startswith("outside_typical_working_hours") for f in result.flags)

    def test_screening_at_11am_not_flagged(self, make_input):
        result = score_behaviour_consistency(
            make_input(screened_at=datetime(2026, 3, 10, 11, 0, tzinfo=timezone.utc))
        )
        assert not any(f.startswith("outside_typical_working_hours") for f in result.flags)


class TestHighVolume:
    def test_over_25_screenings_today_flagged(self, make_input, make_prior):
        priors = [make_prior(screened_at=datetime(2026, 3, 10, 9, i, tzinfo=timezone.utc)) for i in range(26)]
        result = score_behaviour_consistency(
            make_input(screened_at=datetime(2026, 3, 10, 15, 0, tzinfo=timezone.utc), asha_screenings_today=priors)
        )
        assert any(f.startswith("unusually_high_daily_volume") for f in result.flags)


class TestModelOrdering:
    def test_isolation_forest_loads_and_scores_without_crashing(self, make_input):
        """Not asserting an exact score (Isolation Forest output isn't
        deterministic to the decimal across sklearn versions) — just that
        the model loads and produces a valid 0-100 score."""
        result = score_behaviour_consistency(make_input())
        assert 0.0 <= result.score <= 100.0
