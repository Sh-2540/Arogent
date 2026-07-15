"""
Historical Consistency (Arogent Verify signal 2 of 4).

Compares the new reading against this patient's own screening history:
  - Implausible glucose/BMI swings over a short interval
  - Duplicate screenings for the same patient logged suspiciously close
    together (this belongs here, not in Behaviour, because it's about the
    patient's own record — not about the ASHA's broader work pattern)

When a patient has no prior screenings, this signal is UNAVAILABLE rather
than defaulted to a fixed neutral score — aggregate.py excludes unavailable
signals from the weighted average and reweights the remaining three
proportionally, per the project's missing-data principle: missing
information should not be interpreted as suspicious.
"""
from __future__ import annotations

from app.verify.schemas import VerifyInput, SignalResult

GLUCOSE_IMPLAUSIBLE_SWING = 150.0  # mg/dL within a short window
BMI_IMPLAUSIBLE_SWING = 6.0
SHORT_WINDOW_DAYS = 14

DUPLICATE_WINDOW_HOURS = 6


def score_historical_consistency(data: VerifyInput) -> SignalResult:
    prior = data.patient_previous_screenings

    if not prior:
        return SignalResult(score=0.0, available=False, flags=["no_prior_history"])

    most_recent = max(prior, key=lambda s: s.screened_at)
    days_since = (data.screened_at - most_recent.screened_at).days

    score = 100.0
    flags: list[str] = []

    # Duplicate check: another screening for this patient within a few
    # hours is very unlikely to be a legitimate second visit.
    hours_since = (data.screened_at - most_recent.screened_at).total_seconds() / 3600.0
    if 0 <= hours_since < DUPLICATE_WINDOW_HOURS:
        score -= 40
        flags.append(
            f"possible_duplicate_screening: another screening for this patient "
            f"was logged {hours_since:.1f} hours ago"
        )

    # Implausible swing checks, weighted down the further back the
    # comparison point is — a jump vs. a 13-day-old reading is stronger
    # evidence of a problem than the same jump vs. a 6-month-old one.
    if days_since <= SHORT_WINDOW_DAYS:
        recency_weight = 1.0 - (days_since / SHORT_WINDOW_DAYS) * 0.5  # 1.0 -> 0.5 over the window

        glucose_delta = abs(data.blood_glucose_mg_dl - most_recent.blood_glucose_mg_dl)
        if glucose_delta > GLUCOSE_IMPLAUSIBLE_SWING:
            deduction = min(35, (glucose_delta - GLUCOSE_IMPLAUSIBLE_SWING) / 5) * recency_weight
            score -= deduction
            flags.append(
                f"implausible_glucose_swing: {glucose_delta:.0f} mg/dL change from the "
                f"screening {days_since} day(s) ago"
            )

        bmi_delta = abs(data.bmi - most_recent.bmi)
        if bmi_delta > BMI_IMPLAUSIBLE_SWING:
            deduction = min(25, (bmi_delta - BMI_IMPLAUSIBLE_SWING) * 4) * recency_weight
            score -= deduction
            flags.append(
                f"implausible_bmi_swing: {bmi_delta:.1f} change from the screening "
                f"{days_since} day(s) ago"
            )

    if not flags:
        flags.append("consistent_with_screening_history")

    return SignalResult(score=max(score, 0.0), available=True, flags=flags)
