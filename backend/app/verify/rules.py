"""
Clinical Consistency (Arogent Verify signal 1 of 4).

Two layers:
  1. Hard physiological bounds — values outside these are almost certainly
     data entry errors, not clinical edge cases. A violation caps the score
     at 10 and is surfaced as a hard_bound_violation, which aggregate.py
     turns into a NEEDS_REVIEW status regardless of the other three signals.
  2. Soft coherence scoring — for values within bounds, checks whether
     glucose, BMI, symptoms, and family history plausibly fit together.
     This is a small weighted checklist, not a black-box formula, so it
     can be defended line-by-line.
"""
from __future__ import annotations

from app.verify.schemas import VerifyInput, SignalResult

GLUCOSE_HARD_MIN = 40.0
GLUCOSE_HARD_MAX = 600.0
BMI_HARD_MIN = 10.0
BMI_HARD_MAX = 70.0

HARD_BOUND_SCORE = 10.0

SEVERE_SYMPTOMS = {"blurred_vision", "slow_healing_wounds"}


def check_hard_bounds(data: VerifyInput) -> list[str]:
    """Returns a list of violation flags — empty if all values are within
    physiologically plausible range."""
    violations = []
    if not (GLUCOSE_HARD_MIN <= data.blood_glucose_mg_dl <= GLUCOSE_HARD_MAX):
        violations.append(
            f"glucose_out_of_bounds: {data.blood_glucose_mg_dl} mg/dL is outside "
            f"the plausible range ({GLUCOSE_HARD_MIN}-{GLUCOSE_HARD_MAX})"
        )
    if not (BMI_HARD_MIN <= data.bmi <= BMI_HARD_MAX):
        violations.append(
            f"bmi_out_of_bounds: {data.bmi} is outside the plausible range "
            f"({BMI_HARD_MIN}-{BMI_HARD_MAX})"
        )
    return violations


def score_clinical_consistency(data: VerifyInput) -> SignalResult:
    hard_violations = check_hard_bounds(data)
    if hard_violations:
        return SignalResult(score=HARD_BOUND_SCORE, available=True, flags=hard_violations)

    score = 100.0
    flags: list[str] = []

    high_glucose = data.blood_glucose_mg_dl > 200
    normal_glucose = data.blood_glucose_mg_dl < 140
    has_symptoms = len(data.symptoms) > 0
    has_severe_symptoms = any(s in SEVERE_SYMPTOMS for s in data.symptoms)
    elevated_bmi = data.bmi > 27

    # High glucose with none of the corroborating evidence (no symptoms, no
    # family history, normal BMI) — mildly less commonly observed, not
    # impossible. Asymptomatic hyperglycemia genuinely happens, so this is
    # evidence, not proof, and the deduction is small.
    if high_glucose and not has_symptoms and not data.family_history_diabetes and not elevated_bmi:
        score -= 15
        flags.append(
            "high_glucose_no_corroboration: elevated glucose with no symptoms, "
            "family history, or elevated BMI — a less commonly observed combination, "
            "though asymptomatic cases do occur"
        )

    # Severe symptoms reported alongside a normal glucose reading — worth
    # a modest deduction, since severe symptoms are more often associated
    # with more clearly elevated readings, but not a hard contradiction.
    if has_severe_symptoms and normal_glucose:
        score -= 10
        flags.append(
            "severe_symptoms_normal_glucose: severe symptoms reported with a "
            "normal glucose reading — worth a second look, not necessarily an error"
        )

    # Values that reinforce each other add no deduction and are noted as
    # a positive signal for explain.py to surface.
    if high_glucose and (has_symptoms or data.family_history_diabetes or elevated_bmi):
        flags.append("clinical_values_mutually_reinforcing")

    return SignalResult(score=max(score, 0.0), available=True, flags=flags)
