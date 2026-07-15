from app.verify.schemas import SignalResult
from app.verify.explain import build_explanation


def _sr(score: float, available: bool = True, flags=None) -> SignalResult:
    return SignalResult(score=score, available=available, flags=flags or [])


class TestExplanationStructure:
    def test_always_returns_exactly_four_bullets(self):
        explanation = build_explanation(_sr(100), _sr(100), _sr(100), _sr(100))
        assert len(explanation) == 4

    def test_every_bullet_starts_with_its_signal_name(self):
        explanation = build_explanation(
            _sr(100, flags=["clinical_values_mutually_reinforcing"]),
            _sr(100, flags=["consistent_with_screening_history"]),
            _sr(100, flags=["typical_screening_pattern"]),
            _sr(100, flags=["village_matches_assignment"]),
        )
        expected_prefixes = ["Clinical consistency:", "Historical consistency:", "Behaviour consistency:", "Geographic consistency:"]
        assert all(any(bullet.startswith(p) for p in expected_prefixes) for bullet in explanation)

    def test_worst_scoring_signal_appears_first(self):
        explanation = build_explanation(
            _sr(100, flags=["clinical_values_mutually_reinforcing"]),
            _sr(30, flags=["implausible_glucose_swing: 200 mg/dL change from the screening 1 day(s) ago"]),
            _sr(100, flags=["typical_screening_pattern"]),
            _sr(100, flags=["village_matches_assignment"]),
        )
        assert explanation[0].startswith("Historical consistency: Low")

    def test_unavailable_signal_labeled_unavailable_and_sorted_first(self):
        explanation = build_explanation(
            _sr(100, flags=["clinical_values_mutually_reinforcing"]),
            _sr(0, available=False, flags=["no_prior_history"]),
            _sr(100, flags=["typical_screening_pattern"]),
            _sr(100, flags=["village_matches_assignment"]),
        )
        assert explanation[0].startswith("Historical consistency: Unavailable")

    def test_dynamic_flag_detail_is_extracted_and_formatted(self):
        explanation = build_explanation(
            _sr(60, flags=["high_glucose_no_corroboration: elevated glucose with no symptoms"]),
            _sr(100, flags=["consistent_with_screening_history"]),
            _sr(100, flags=["typical_screening_pattern"]),
            _sr(100, flags=["village_matches_assignment"]),
        )
        clinical_bullet = next(b for b in explanation if b.startswith("Clinical consistency"))
        assert "Elevated glucose with no symptoms" in clinical_bullet

    def test_static_flag_uses_lookup_table(self):
        explanation = build_explanation(
            _sr(100, flags=["clinical_values_mutually_reinforcing"]),
            _sr(100, flags=["consistent_with_screening_history"]),
            _sr(100, flags=["typical_screening_pattern"]),
            _sr(100, flags=["village_matches_assignment"]),
        )
        clinical_bullet = next(b for b in explanation if b.startswith("Clinical consistency"))
        assert "mutually consistent" in clinical_bullet
