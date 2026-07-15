from app.core.enums import ConfidenceStatus
from app.verify.schemas import SignalResult
from app.verify.aggregate import compute_confidence_score, determine_status, determine_recommendation


def _sr(score: float, available: bool = True) -> SignalResult:
    return SignalResult(score=score, available=available, flags=[])


class TestProportionalReweighting:
    def test_all_available_uses_documented_weights(self):
        # 100/100/100/100 with any weighting should be 100
        score, _ = compute_confidence_score(_sr(100), _sr(100), _sr(100), _sr(100))
        assert score == 100.0

    def test_unavailable_historical_excluded_and_others_reweighted(self):
        # Only clinical=100, behaviour=100, geographic=100 available (weights .35+.20+.15=.70)
        # historical unavailable and score should NOT drag the average down at all.
        score, breakdown = compute_confidence_score(
            _sr(100), _sr(0, available=False), _sr(100), _sr(100)
        )
        assert score == 100.0  # missing signal must not reduce confidence
        # Breakdown still shows the raw (unused) score for display purposes
        assert breakdown.historical_consistency_score == 0.0

    def test_missing_signal_does_not_equal_treating_it_as_zero(self):
        with_history_low = compute_confidence_score(_sr(100), _sr(20), _sr(100), _sr(100))[0]
        without_history = compute_confidence_score(_sr(100), _sr(20, available=False), _sr(100), _sr(100))[0]
        assert without_history > with_history_low


class TestStatusThresholds:
    def test_score_above_80_is_high(self):
        assert determine_status(80.1, hard_bound_violation=False) == ConfidenceStatus.HIGH

    def test_score_exactly_80_is_medium_not_high(self):
        # Documented explicitly: strictly greater than 80 for HIGH, no ambiguity at the boundary
        assert determine_status(80.0, hard_bound_violation=False) == ConfidenceStatus.MEDIUM

    def test_score_exactly_50_is_medium(self):
        assert determine_status(50.0, hard_bound_violation=False) == ConfidenceStatus.MEDIUM

    def test_score_below_50_is_low(self):
        assert determine_status(49.9, hard_bound_violation=False) == ConfidenceStatus.LOW

    def test_hard_bound_violation_always_needs_review_even_if_score_high(self):
        assert determine_status(95.0, hard_bound_violation=True) == ConfidenceStatus.NEEDS_REVIEW


class TestRecommendation:
    def test_high_recommends_proceed_to_risk_prediction(self):
        assert determine_recommendation(ConfidenceStatus.HIGH) == "Proceed to Risk Prediction"

    def test_medium_recommends_repeat_screening(self):
        assert determine_recommendation(ConfidenceStatus.MEDIUM) == "Repeat Screening"

    def test_low_recommends_repeat_screening(self):
        assert determine_recommendation(ConfidenceStatus.LOW) == "Repeat Screening"

    def test_needs_review_recommends_escalation(self):
        assert determine_recommendation(ConfidenceStatus.NEEDS_REVIEW) == "Escalate for PHC Review"
