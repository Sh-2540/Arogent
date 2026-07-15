"""
Aggregates the four signal results into a final confidence score, status,
and recommendation.

Missing-data principle (applies project-wide, not just here): missing
optional signals do not reduce confidence directly. Available signals are
reweighted proportionally so missing information is never interpreted as
suspicious. In practice, only Historical Consistency can be genuinely
UNAVAILABLE (a patient's first-ever screening) — Behaviour and Geographic
always produce a real, if less precise, score (see their respective
modules for how each handles partial data).

Confidence scoring here is fully deterministic and reproducible from the
same inputs — no generative AI participates in scoring. An LLM is used
only downstream (see explain.py's docstring) to optionally rephrase the
deterministic explanation bullets for tone; it never changes the
underlying reasoning or the score itself.
"""
from __future__ import annotations

from app.core.enums import ConfidenceStatus
from app.verify.schemas import SignalResult, ConfidenceBreakdown

# Base weights when all four signals are available. Sum to 1.0.
BASE_WEIGHTS = {
    "clinical": 0.35,
    "historical": 0.30,
    "behaviour": 0.20,
    "geographic": 0.15,
}

CONFIDENCE_HIGH_THRESHOLD = 80.0  # score > this -> HIGH (strictly greater, no ambiguity at the boundary)
CONFIDENCE_MEDIUM_THRESHOLD = 50.0  # score >= this -> MEDIUM


def compute_confidence_score(
    clinical: SignalResult,
    historical: SignalResult,
    behaviour: SignalResult,
    geographic: SignalResult,
) -> tuple[float, ConfidenceBreakdown]:
    """
    Weighted average over whatever signals are available, with weights
    renormalized to sum to 1.0 over just those signals — this is the
    proportional reweighting the missing-data principle requires.
    """
    signals = {
        "clinical": clinical,
        "historical": historical,
        "behaviour": behaviour,
        "geographic": geographic,
    }

    available_weight_sum = sum(BASE_WEIGHTS[name] for name, s in signals.items() if s.available)
    if available_weight_sum == 0:
        # Should never happen in practice (clinical/behaviour/geographic are
        # always available), but fail safe rather than divide by zero.
        available_weight_sum = 1.0

    confidence_score = 0.0
    for name, signal in signals.items():
        if signal.available:
            renormalized_weight = BASE_WEIGHTS[name] / available_weight_sum
            confidence_score += renormalized_weight * signal.score

    breakdown = ConfidenceBreakdown(
        clinical_consistency_score=clinical.score,
        historical_consistency_score=historical.score,
        behaviour_consistency_score=behaviour.score,
        geographic_consistency_score=geographic.score,
    )

    return round(confidence_score, 1), breakdown


def determine_status(confidence_score: float, hard_bound_violation: bool) -> ConfidenceStatus:
    """NEEDS_REVIEW is reserved specifically for hard-bound violations — a
    distinct signal from a merely low weighted score, so the UI can tell
    'this data is impossible' apart from 'this data is just unusual'."""
    if hard_bound_violation:
        return ConfidenceStatus.NEEDS_REVIEW
    if confidence_score > CONFIDENCE_HIGH_THRESHOLD:
        return ConfidenceStatus.HIGH
    if confidence_score >= CONFIDENCE_MEDIUM_THRESHOLD:
        return ConfidenceStatus.MEDIUM
    return ConfidenceStatus.LOW


def determine_recommendation(status: ConfidenceStatus) -> str:
    """Three categories matching real healthcare workflows — not just
    'proceed' vs. 'don't'."""
    if status == ConfidenceStatus.NEEDS_REVIEW:
        return "Escalate for PHC Review"
    if status == ConfidenceStatus.HIGH:
        return "Proceed to Risk Prediction"
    return "Repeat Screening"  # MEDIUM or LOW
