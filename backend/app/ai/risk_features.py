"""
Feature engineering for Arogent Risk — shared between training
(app/ai/train_risk_model.py) and runtime (app/risk/features.py) so the two
can never drift apart.

Feature order (must match exactly wherever a raw feature vector is built):
    [age, bmi, blood_glucose_mg_dl, family_history_diabetes,
     activity_low, activity_high, symptom_count,
     has_fatigue, has_frequent_urination, has_excessive_thirst,
     has_blurred_vision, has_slow_healing_wounds]

activity_low/activity_high are one-hot encoded from physical_activity_level
(MODERATE is the implicit baseline — both 0). Individual symptom flags are
included, not just a count, so per-prediction feature contributions (see
app/risk/features.py) can say *which* symptom mattered, not just "some
symptom was present."
"""
from __future__ import annotations

import numpy as np

from app.ai.synthetic_data import SYMPTOM_POOL

RISK_FEATURE_NAMES = [
    "age",
    "bmi",
    "blood_glucose_mg_dl",
    "family_history_diabetes",
    "activity_low",
    "activity_high",
    "symptom_count",
    "has_fatigue",
    "has_frequent_urination",
    "has_excessive_thirst",
    "has_blurred_vision",
    "has_slow_healing_wounds",
]

# Human-readable labels for the UI / explanation output.
RISK_FEATURE_DISPLAY_NAMES = {
    "age": "Age",
    "bmi": "BMI",
    "blood_glucose_mg_dl": "Blood glucose",
    "family_history_diabetes": "Family history of diabetes",
    "activity_low": "Low physical activity",
    "activity_high": "High physical activity",
    "symptom_count": "Number of symptoms reported",
    "has_fatigue": "Fatigue",
    "has_frequent_urination": "Frequent urination",
    "has_excessive_thirst": "Excessive thirst",
    "has_blurred_vision": "Blurred vision",
    "has_slow_healing_wounds": "Slow-healing wounds",
}


def build_feature_vector(
    age: int,
    bmi: float,
    blood_glucose_mg_dl: float,
    family_history_diabetes: bool,
    physical_activity_level: str,
    symptoms: list[str],
) -> np.ndarray:
    """Builds a single feature row in RISK_FEATURE_NAMES order. Used both
    at training time (over the synthetic dataset) and at runtime
    (app/risk/features.py, over a real screening)."""
    activity_low = 1.0 if physical_activity_level == "LOW" else 0.0
    activity_high = 1.0 if physical_activity_level == "HIGH" else 0.0

    symptom_set = set(symptoms)
    symptom_flags = [1.0 if s in symptom_set else 0.0 for s in SYMPTOM_POOL]

    row = [
        float(age),
        float(bmi),
        float(blood_glucose_mg_dl),
        1.0 if family_history_diabetes else 0.0,
        activity_low,
        activity_high,
        float(len(symptoms)),
        *symptom_flags,
    ]
    return np.array(row, dtype=float)
