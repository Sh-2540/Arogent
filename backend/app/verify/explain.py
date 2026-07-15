"""
Turns signal scores and flags into human-readable explanation bullets.

This is fully deterministic and template-based — NOT an LLM call. That's
a deliberate Responsible AI choice: confidence scoring and its explanation
must be reproducible from the same inputs every time. An optional LLM layer
(see app/config.py's tech stack notes) may be used elsewhere in the product
to rephrase these bullets for tone when shown to an ASHA worker, but it
never generates the underlying reasoning and never runs before this module.

Each bullet leads with the signal name and level ("Clinical consistency:
High.") followed by one plain-language sentence — this format was chosen
specifically so the Result screen can be scanned quickly rather than read
as a paragraph.

Capped at 4 bullets (one per signal) so it never becomes a wall of text.
The worst-scoring signal's reason is always included first.
"""
from __future__ import annotations

from app.verify.schemas import SignalResult


def _level_label(score: float) -> str:
    if score >= 80:
        return "High"
    if score >= 50:
        return "Medium"
    return "Low"


_SIGNAL_DISPLAY_NAMES = {
    "clinical": "Clinical consistency",
    "historical": "Historical consistency",
    "behaviour": "Behaviour consistency",
    "geographic": "Geographic consistency",
}

# One human-readable detail sentence per flag. Flags not in this table
# (defensive — every flag emitted by the signal modules should have an
# entry) fall back to a generic sentence rather than crashing.
_FLAG_DETAILS: dict[str, str] = {
    "clinical_values_mutually_reinforcing": "Glucose, BMI, and reported symptoms are mutually consistent.",
    "high_glucose_no_corroboration": "Elevated glucose has no corroborating symptoms, family history, or BMI — worth a second look, though asymptomatic cases do occur.",
    "severe_symptoms_normal_glucose": "Severe symptoms were reported alongside a normal glucose reading.",
    "glucose_out_of_bounds": "The glucose reading is outside the physiologically plausible range.",
    "bmi_out_of_bounds": "The BMI value is outside the physiologically plausible range.",

    "no_prior_history": "This is the patient's first recorded screening, so there's no history to compare against.",
    "consistent_with_screening_history": "This reading is consistent with the patient's screening history.",
    "possible_duplicate_screening": "Another screening for this patient was logged only hours ago.",
    "implausible_glucose_swing": "Glucose has changed sharply since the patient's last screening.",
    "implausible_bmi_swing": "BMI has changed sharply since the patient's last screening.",

    "typical_screening_pattern": "This ASHA's screening pace and pattern today is typical.",
    "rapid_screening_pace": "This screening was logged unusually soon after the ASHA's previous one today.",
    "outside_typical_working_hours": "This screening was logged outside typical working hours.",
    "unusually_high_daily_volume": "This ASHA has logged an unusually high number of screenings today.",
    "anomaly_model_flagged_unusual_pattern": "The pattern of readings for this ASHA today is statistically unusual.",
    "anomaly_model_slightly_unusual": "The pattern of readings for this ASHA today is somewhat atypical, though not strongly flagged.",

    "village_matches_assignment": "Screening location matches the ASHA's assigned village.",
    "village_mismatch": "Screening location does not match the ASHA's assigned village.",
    "outside_service_region": "Screening location is further from the assigned service region than expected.",
    "gps_unavailable": "GPS coordinates were unavailable — location was checked by village name only.",
}


def _detail_for_flag(flag: str) -> str:
    """
    Signal modules emit two kinds of flags:
      - static, e.g. "typical_screening_pattern" (no colon) -> looked up in
        _FLAG_DETAILS directly
      - dynamic, e.g. "implausible_glucose_swing: 185 mg/dL change from..."
        -> the text after the colon IS the detail sentence already; using
        it directly is more informative than a generic template, since it
        carries the actual numbers behind the flag.
    """
    if ":" in flag:
        _, _, detail = flag.partition(":")
        detail = detail.strip()
        if detail:
            detail = detail[0].upper() + detail[1:]
            if not detail.endswith("."):
                detail += "."
            return detail
    return _FLAG_DETAILS.get(flag, "No specific concerns were identified.")


def _bullet_for_signal(key: str, signal: SignalResult) -> str:
    display_name = _SIGNAL_DISPLAY_NAMES[key]
    level = "Unavailable" if not signal.available else _level_label(signal.score)

    if not signal.available:
        detail = _detail_for_flag(signal.flags[0]) if signal.flags else "Not enough data was available for this signal."
    else:
        detail_flag = signal.flags[0] if signal.flags else None
        detail = _detail_for_flag(detail_flag) if detail_flag else "No specific concerns were identified."

    return f"{display_name}: {level}. {detail}"


def build_explanation(
    clinical: SignalResult,
    historical: SignalResult,
    behaviour: SignalResult,
    geographic: SignalResult,
) -> list[str]:
    signals = {
        "clinical": clinical,
        "historical": historical,
        "behaviour": behaviour,
        "geographic": geographic,
    }

    # Sort so the worst-scoring (or unavailable) signal's bullet comes first —
    # that's the most actionable information for an ASHA worker or PHC officer.
    def sort_key(item: tuple[str, SignalResult]) -> float:
        _, signal = item
        return -1.0 if not signal.available else signal.score

    ordered = sorted(signals.items(), key=sort_key)

    return [_bullet_for_signal(key, signal) for key, signal in ordered]
