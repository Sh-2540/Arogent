"""
Trains the Isolation Forest used by Arogent Verify's Behaviour Consistency
signal (app/verify/anomaly.py).

This is an OFFLINE script — run once (or whenever the synthetic dataset
changes) to produce `models/behaviour_isolation_forest.joblib` and
`models/behaviour_feature_means.json`. Nothing here runs at request time;
`app/verify/anomaly.py` only loads these artifacts.

Feature vector per screening (must match app/verify/anomaly.py exactly):
    [blood_glucose_mg_dl, bmi, minutes_since_asha_previous_screening_today,
     screenings_by_asha_today_so_far, glucose_stddev_asha_today, hour_of_day]
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import numpy as np
from sklearn.ensemble import IsolationForest
import joblib

from app.ai.synthetic_data import generate_screening_dataset, SyntheticScreening

MODELS_DIR = Path(__file__).parent / "models"
FOREST_PATH = MODELS_DIR / "behaviour_isolation_forest.joblib"
FEATURE_MEANS_PATH = MODELS_DIR / "behaviour_feature_means.json"

FEATURE_NAMES = [
    "blood_glucose_mg_dl",
    "bmi",
    "minutes_since_asha_previous_screening_today",
    "screenings_by_asha_today_so_far",
    "glucose_stddev_asha_today",
    "hour_of_day",
]


def build_feature_matrix(records: list[SyntheticScreening]) -> tuple[np.ndarray, list[bool]]:
    """
    Walks the (already time-ordered) synthetic records and computes, for each
    screening, the same sequential per-ASHA-per-day features that
    app/verify/anomaly.py computes at request time.
    """
    # Group by (asha_id, date) preserving order
    by_asha_day: dict[tuple[int, str], list[SyntheticScreening]] = defaultdict(list)
    for r in records:
        key = (r.asha_id, r.screened_at.date().isoformat())
        by_asha_day[key].append(r)

    rows: list[list[float]] = []
    labels: list[bool] = []  # True = anomalous (ground truth, for evaluation only)

    for _, day_records in by_asha_day.items():
        day_records.sort(key=lambda r: r.screened_at)
        glucose_so_far: list[float] = []

        for i, r in enumerate(day_records):
            minutes_since_prev = (
                (r.screened_at - day_records[i - 1].screened_at).total_seconds() / 60.0
                if i > 0
                else 30.0  # first screening of the day: assume a typical gap, not zero
            )
            glucose_so_far.append(r.blood_glucose_mg_dl)
            glucose_stddev = float(np.std(glucose_so_far)) if len(glucose_so_far) > 1 else -1.0
            # -1.0 sentinel: "not enough data yet" — replaced with population mean below

            rows.append([
                r.blood_glucose_mg_dl,
                r.bmi,
                minutes_since_prev,
                i + 1,  # screenings by this ASHA today so far, 1-indexed
                glucose_stddev,
                r.screened_at.hour,
            ])
            labels.append(r.is_anomalous_day)

    matrix = np.array(rows, dtype=float)

    # Impute the -1.0 sentinel (glucose_stddev undefined on a worker's first
    # screening of the day) with the population mean of defined values —
    # this is the same imputation rule anomaly.py applies at request time.
    stddev_col = matrix[:, 4]
    defined_mask = stddev_col != -1.0
    population_mean_stddev = stddev_col[defined_mask].mean()
    matrix[~defined_mask, 4] = population_mean_stddev

    return matrix, labels


def train_and_save() -> None:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    records = generate_screening_dataset()
    X, labels = build_feature_matrix(records)

    contamination = sum(labels) / len(labels)
    contamination = float(np.clip(contamination, 0.01, 0.5))

    model = IsolationForest(
        n_estimators=200,
        contamination=contamination,
        random_state=42,
    )
    model.fit(X)

    joblib.dump(model, FOREST_PATH)

    feature_means = {name: float(X[:, i].mean()) for i, name in enumerate(FEATURE_NAMES)}
    FEATURE_MEANS_PATH.write_text(json.dumps(feature_means, indent=2))

    # Quick offline sanity check — anomalous records should score lower
    # (more anomalous) on average than normal ones. This isn't a unit test
    # (model output isn't deterministic to the decimal) but a training-time
    # sanity print so a broken feature pipeline is caught immediately.
    scores = model.decision_function(X)
    labels_arr = np.array(labels)
    normal_mean = scores[~labels_arr].mean()
    anomalous_mean = scores[labels_arr].mean()
    print(f"Trained on {len(X)} screenings.")
    print(f"Mean anomaly score — normal: {normal_mean:.3f}, anomalous: {anomalous_mean:.3f}")
    assert anomalous_mean < normal_mean, (
        "Sanity check failed: anomalous records should score lower than normal ones. "
        "Check the feature engineering pipeline before using this model."
    )
    print(f"Saved model to {FOREST_PATH}")
    print(f"Saved feature means to {FEATURE_MEANS_PATH}")


if __name__ == "__main__":
    train_and_save()
