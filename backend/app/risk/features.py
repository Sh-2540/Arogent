"""
Runtime feature building and per-prediction explainability for Arogent Risk.

build_feature_vector is a thin wrapper around app.ai.risk_features so
training and runtime can never drift apart — this module only adds the
per-prediction contribution logic on top.
"""
from __future__ import annotations

import numpy as np

from app.ai.risk_features import (
    build_feature_vector as _build_feature_vector,
    RISK_FEATURE_NAMES,
    RISK_FEATURE_DISPLAY_NAMES,
)
from app.risk.schemas import RiskInput, FeatureContribution

TOP_N_CONTRIBUTING_FEATURES = 5


def build_feature_vector(data: RiskInput) -> np.ndarray:
    return _build_feature_vector(
        age=data.age,
        bmi=data.bmi,
        blood_glucose_mg_dl=data.blood_glucose_mg_dl,
        family_history_diabetes=data.family_history_diabetes,
        physical_activity_level=data.physical_activity_level,
        symptoms=data.symptoms,
    )


def compute_logistic_regression_contributions(
    model, scaler, raw_feature_vector: np.ndarray
) -> list[FeatureContribution]:
    """
    Per-PREDICTION contribution, not just global importance: for a logistic
    regression, each feature's contribution to this specific prediction's
    log-odds is coefficient * standardized_value. This is a real,
    case-specific explanation — it can say "for THIS patient, glucose
    pushed risk up" rather than only "glucose matters in general."
    """
    scaled = scaler.transform(raw_feature_vector.reshape(1, -1))[0]
    coefficients = model.coef_[0]
    contributions = coefficients * scaled

    ranked_indices = np.argsort(-np.abs(contributions))[:TOP_N_CONTRIBUTING_FEATURES]

    results = []
    for i in ranked_indices:
        name = RISK_FEATURE_NAMES[i]
        value = contributions[i]
        direction = "increases_risk" if value > 0 else ("decreases_risk" if value < 0 else "unspecified")
        results.append(
            FeatureContribution(
                feature=name,
                display_name=RISK_FEATURE_DISPLAY_NAMES[name],
                contribution=round(float(value), 4),
                direction=direction,
            )
        )
    return results


def compute_global_importance_contributions(
    feature_importance_metadata: dict,
) -> list[FeatureContribution]:
    """
    Fallback used only if the deployed model is ever XGBoost: per-prediction
    SHAP-style explanations are roadmap, not MVP (a defensible hackathon
    simplification — noted explicitly rather than left implicit). Falls
    back to the model's GLOBAL feature importance ranking instead, which is
    still useful but not case-specific the way the Logistic Regression path
    above is.
    """
    ranked = feature_importance_metadata["ranked_features"][:TOP_N_CONTRIBUTING_FEATURES]
    return [
        FeatureContribution(
            feature=f["feature"],
            display_name=f["display_name"],
            contribution=f["importance"],
            direction="unspecified",  # global importance has no sign/direction
        )
        for f in ranked
    ]
