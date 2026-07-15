"""
Loads the model artifacts produced by app/ai/train_risk_model.py and
exposes a single predict() call. Which model type was actually chosen
(LogisticRegression vs XGBoost) is read from risk_model_metadata.json —
this module doesn't hardcode an assumption about which one won.
"""
from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np

MODELS_DIR = Path(__file__).parent.parent / "ai" / "models"
MODEL_PATH = MODELS_DIR / "risk_model.joblib"
SCALER_PATH = MODELS_DIR / "risk_scaler.joblib"
METADATA_PATH = MODELS_DIR / "risk_model_metadata.json"
FEATURE_IMPORTANCE_PATH = MODELS_DIR / "risk_feature_importance.json"

_model = None
_scaler = None
_metadata: dict | None = None
_feature_importance: dict | None = None


def _load():
    global _model, _scaler, _metadata, _feature_importance
    if _model is None:
        if not MODEL_PATH.exists():
            raise RuntimeError(
                f"Risk model not found at {MODEL_PATH}. "
                "Run `python -m app.ai.train_risk_model` first."
            )
        _model = joblib.load(MODEL_PATH)
        _scaler = joblib.load(SCALER_PATH)
        _metadata = json.loads(METADATA_PATH.read_text())
        _feature_importance = json.loads(FEATURE_IMPORTANCE_PATH.read_text())
    return _model, _scaler, _metadata, _feature_importance


def predict_probability(raw_feature_vector: np.ndarray) -> float:
    """Returns the predicted probability of diabetes risk, 0.0-1.0.
    Handles both model types: Logistic Regression needs scaled features,
    XGBoost does not, but scaling XGBoost's input is harmless (tree splits
    are scale-invariant) so we scale unconditionally for simplicity."""
    model, scaler, metadata, _ = _load()
    scaled = scaler.transform(raw_feature_vector.reshape(1, -1))
    return float(model.predict_proba(scaled)[0, 1])


def get_model_and_scaler():
    model, scaler, _, _ = _load()
    return model, scaler


def get_metadata() -> dict:
    _, _, metadata, _ = _load()
    return metadata


def get_feature_importance() -> dict:
    _, _, _, feature_importance = _load()
    return feature_importance


def is_logistic_regression() -> bool:
    metadata = get_metadata()
    return metadata["model_used"] == "LogisticRegression"
