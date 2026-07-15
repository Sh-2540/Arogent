"""
Trains Arogent Risk's diabetes prediction model.

Per the approved design: start with Logistic Regression as the
interpretable baseline, compare against XGBoost, and only adopt XGBoost
if it provides a MEANINGFUL improvement (>= XGBOOST_IMPROVEMENT_THRESHOLD
AUC) on a held-out validation split. Otherwise keep Logistic Regression,
since its per-feature coefficients give a much more direct, defensible
explanation for a healthcare decision-support tool than XGBoost's
feature_importances_ would.

Trained ONLY on records from days that were not anomalous in the synthetic
generator — this mirrors the production rule that Arogent Risk only ever
sees screenings that passed Arogent Verify at HIGH confidence, so it
shouldn't be trained on the kind of low-quality data it will never
actually receive.

Outputs (to app/ai/models/):
    risk_model.joblib              — the chosen model (LogisticRegression or XGBClassifier)
    risk_scaler.joblib             — StandardScaler fit on training features (used by both model types for consistency)
    risk_model_metadata.json       — which model was chosen, why, and validation metrics
    risk_feature_importance.json   — global feature importance/coefficients for the chosen model
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, accuracy_score
from xgboost import XGBClassifier

from app.ai.synthetic_data import generate_screening_dataset
from app.ai.risk_features import build_feature_vector, RISK_FEATURE_NAMES, RISK_FEATURE_DISPLAY_NAMES

MODELS_DIR = Path(__file__).parent / "models"
MODEL_PATH = MODELS_DIR / "risk_model.joblib"
SCALER_PATH = MODELS_DIR / "risk_scaler.joblib"
METADATA_PATH = MODELS_DIR / "risk_model_metadata.json"
FEATURE_IMPORTANCE_PATH = MODELS_DIR / "risk_feature_importance.json"

XGBOOST_IMPROVEMENT_THRESHOLD = 0.02  # AUC points; below this, keep the interpretable baseline
RANDOM_SEED = 42


def build_training_data():
    records = generate_screening_dataset()
    # Arogent Risk never sees screenings from an anomalous day in production
    # (they'd fail Arogent Verify first) — don't train on them either.
    clean_records = [r for r in records if not r.is_anomalous_day]

    rng = np.random.default_rng(RANDOM_SEED)
    X = np.array([
        build_feature_vector(
            age=r.age, bmi=r.bmi, blood_glucose_mg_dl=r.blood_glucose_mg_dl,
            family_history_diabetes=r.family_history_diabetes,
            physical_activity_level=r.physical_activity_level, symptoms=r.symptoms,
        )
        for r in clean_records
    ])
    # Probabilistic labels (not a hard threshold) — a more realistic, noisier
    # classification problem than thresholding true_diabetes_risk directly.
    y = np.array([1 if rng.random() < r.true_diabetes_risk else 0 for r in clean_records])

    return X, y


def train_and_save() -> None:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    X, y = build_training_data()
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_SEED, stratify=y
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)

    # --- Baseline: Logistic Regression ---
    logreg = LogisticRegression(max_iter=1000, random_state=RANDOM_SEED)
    logreg.fit(X_train_scaled, y_train)
    logreg_val_proba = logreg.predict_proba(X_val_scaled)[:, 1]
    logreg_auc = roc_auc_score(y_val, logreg_val_proba)
    logreg_acc = accuracy_score(y_val, logreg_val_proba > 0.5)

    # --- Comparison: XGBoost ---
    # XGBoost doesn't need scaled features, but we score it on the same
    # validation split for a fair AUC comparison. Using unscaled X_train/X_val
    # here since XGBoost is scale-invariant (tree splits don't care).
    xgb = XGBClassifier(
        n_estimators=100, max_depth=3, learning_rate=0.1,
        random_state=RANDOM_SEED, eval_metric="logloss",
    )
    xgb.fit(X_train, y_train)
    xgb_val_proba = xgb.predict_proba(X_val)[:, 1]
    xgb_auc = roc_auc_score(y_val, xgb_val_proba)
    xgb_acc = accuracy_score(y_val, xgb_val_proba > 0.5)

    improvement = xgb_auc - logreg_auc
    use_xgboost = improvement >= XGBOOST_IMPROVEMENT_THRESHOLD

    chosen_model = xgb if use_xgboost else logreg
    chosen_name = "XGBoost" if use_xgboost else "LogisticRegression"

    joblib.dump(chosen_model, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)  # saved regardless — runtime always scales, model.py decides whether to use it

    # Global feature importance for whichever model was chosen — used for
    # the "important contributing features" requirement in the UI, and as
    # the fallback explanation source if XGBoost is ever chosen (see
    # app/risk/features.py for per-prediction contributions when
    # LogisticRegression is the deployed model).
    if use_xgboost:
        importances = chosen_model.feature_importances_
    else:
        importances = np.abs(chosen_model.coef_[0])
    importance_ranked = sorted(
        zip(RISK_FEATURE_NAMES, importances.tolist(), strict=True), key=lambda x: -x[1]
    )
    feature_importance = {
        "model_used": chosen_name,
        "ranked_features": [
            {"feature": name, "display_name": RISK_FEATURE_DISPLAY_NAMES[name], "importance": round(imp, 4)}
            for name, imp in importance_ranked
        ],
    }
    FEATURE_IMPORTANCE_PATH.write_text(json.dumps(feature_importance, indent=2))

    metadata = {
        "model_used": chosen_name,
        "reason": (
            f"XGBoost validation AUC ({xgb_auc:.4f}) exceeded Logistic Regression "
            f"({logreg_auc:.4f}) by {improvement:.4f}, at or above the "
            f"{XGBOOST_IMPROVEMENT_THRESHOLD} threshold for adopting the less "
            f"interpretable model."
            if use_xgboost else
            f"XGBoost validation AUC ({xgb_auc:.4f}) did not meaningfully exceed "
            f"Logistic Regression ({logreg_auc:.4f}) — improvement of {improvement:.4f} "
            f"is below the {XGBOOST_IMPROVEMENT_THRESHOLD} threshold, so the more "
            f"interpretable Logistic Regression baseline is deployed."
        ),
        "validation_metrics": {
            "logistic_regression": {"auc": round(logreg_auc, 4), "accuracy": round(logreg_acc, 4)},
            "xgboost": {"auc": round(xgb_auc, 4), "accuracy": round(xgb_acc, 4)},
        },
        "training_set_size": int(len(X_train)),
        "validation_set_size": int(len(X_val)),
        "note": (
            "Confidence score calibration against clinically validated screening "
            "outcomes is part of the production roadmap and is not included in "
            "this hackathon MVP — these metrics are against a synthetic validation "
            "split only. Individual per-prediction feature contributions can "
            "occasionally show a counterintuitive sign (e.g. a symptom appearing "
            "to slightly decrease risk) due to correlation between features in a "
            "modestly-sized synthetic training set — a known characteristic of "
            "linear models with correlated inputs, not a bug. Production "
            "deployment would use a larger, real (de-identified) dataset with "
            "multicollinearity diagnostics before relying on individual "
            "coefficients for clinical explanation."
        ),
    }
    METADATA_PATH.write_text(json.dumps(metadata, indent=2))

    print(f"Logistic Regression — AUC: {logreg_auc:.4f}, Accuracy: {logreg_acc:.4f}")
    print(f"XGBoost             — AUC: {xgb_auc:.4f}, Accuracy: {xgb_acc:.4f}")
    print(f"Improvement: {improvement:.4f} (threshold: {XGBOOST_IMPROVEMENT_THRESHOLD})")
    print(f"Deployed model: {chosen_name}")
    print(f"Saved to {MODEL_PATH}, {SCALER_PATH}, {METADATA_PATH}, {FEATURE_IMPORTANCE_PATH}")


if __name__ == "__main__":
    train_and_save()
