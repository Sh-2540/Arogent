"""
Behaviour Consistency (Arogent Verify signal 3 of 4).

Combines two things, not the Isolation Forest alone:
  1. Deterministic workflow metrics — screening pace and working-hours
     timing, both hand-checkable and easy to defend to a judge
  2. An Isolation Forest anomaly score over the same features plus glucose/
     BMI variance, which catches subtler multivariate patterns a fixed
     rule wouldn't (e.g. suspiciously uniform readings across patients)

The two are blended (not just averaged blindly) — deterministic checks can
independently push the score down even if the learned model doesn't flag
anything, since an obviously-too-fast pace shouldn't need ML to catch.

This module only LOADS a fitted model. Training happens offline in
app/ai/train_anomaly_model.py — see that file for the feature engineering
this module's runtime feature vector must match exactly.
"""
from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np

from app.verify.schemas import VerifyInput, SignalResult

MODELS_DIR = Path(__file__).parent.parent / "ai" / "models"
FOREST_PATH = MODELS_DIR / "behaviour_isolation_forest.joblib"
FEATURE_MEANS_PATH = MODELS_DIR / "behaviour_feature_means.json"

RAPID_FIRE_MINUTES_THRESHOLD = 5.0
WORKING_HOUR_START = 8
WORKING_HOUR_END = 19

_model = None
_feature_means: dict[str, float] | None = None


def _load_model():
    """Lazy-loaded singleton so the joblib file is only read once per process,
    not on every request."""
    global _model, _feature_means
    if _model is None:
        if not FOREST_PATH.exists():
            raise RuntimeError(
                f"Behaviour model not found at {FOREST_PATH}. "
                "Run `python -m app.ai.train_anomaly_model` first."
            )
        _model = joblib.load(FOREST_PATH)
        _feature_means = json.loads(FEATURE_MEANS_PATH.read_text())
    return _model, _feature_means


def _normalize_anomaly_score(raw_score: float) -> float:
    """Isolation Forest's decision_function returns roughly [-0.5, 0.5],
    positive = more normal. Map to a 0-100 scale, clipped defensively
    since real-world inputs can fall outside the training distribution."""
    normalized = (raw_score + 0.5) * 100.0
    return float(np.clip(normalized, 0.0, 100.0))


def score_behaviour_consistency(data: VerifyInput) -> SignalResult:
    flags: list[str] = []
    deterministic_score = 100.0

    today_screenings = data.asha_screenings_today  # already time-ordered by service.py
    n_today = len(today_screenings) + 1  # +1 to include the current one being scored

    minutes_since_prev: float
    if today_screenings:
        most_recent = today_screenings[-1]
        minutes_since_prev = (data.screened_at - most_recent.screened_at).total_seconds() / 60.0
        if minutes_since_prev < RAPID_FIRE_MINUTES_THRESHOLD:
            deterministic_score -= 35
            flags.append(
                f"rapid_screening_pace: only {minutes_since_prev:.1f} minutes since this "
                f"ASHA's previous screening today"
            )
    else:
        minutes_since_prev = 30.0  # first screening of the day: assume a typical gap

    if not (WORKING_HOUR_START <= data.screened_at.hour < WORKING_HOUR_END):
        deterministic_score -= 15
        flags.append(f"outside_typical_working_hours: screened at {data.screened_at.strftime('%H:%M')}")

    if n_today > 25:
        deterministic_score -= 20
        flags.append(f"unusually_high_daily_volume: {n_today} screenings by this ASHA today")

    deterministic_score = max(deterministic_score, 0.0)

    # --- Isolation Forest component ---
    model, feature_means = _load_model()

    glucose_values = [s.blood_glucose_mg_dl for s in today_screenings] + [data.blood_glucose_mg_dl]
    glucose_stddev = float(np.std(glucose_values)) if len(glucose_values) > 1 else feature_means["glucose_stddev_asha_today"]

    feature_vector = np.array([[
        data.blood_glucose_mg_dl,
        data.bmi,
        minutes_since_prev,
        n_today,
        glucose_stddev,
        data.screened_at.hour,
    ]])

    raw_anomaly_score = model.decision_function(feature_vector)[0]
    ml_score = _normalize_anomaly_score(raw_anomaly_score)

    if ml_score < 40:
        flags.append("anomaly_model_flagged_unusual_pattern")
    elif ml_score < 75:
        flags.append("anomaly_model_slightly_unusual")

    # Blend: the ML score can pull a clean deterministic score down (it catches
    # subtler patterns rules don't), but a deterministic violation is never
    # diluted upward by a model that happened not to flag it — we always take
    # the more suspicious (lower) of the two readings.
    blended = 0.5 * deterministic_score + 0.5 * ml_score
    combined_score = min(deterministic_score, blended)

    if not flags:
        flags.append("typical_screening_pattern")

    return SignalResult(score=max(combined_score, 0.0), available=True, flags=flags)
