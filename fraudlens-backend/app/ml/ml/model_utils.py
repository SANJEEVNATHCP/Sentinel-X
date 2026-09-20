"""Paths and persisted model loading."""

from pathlib import Path
from typing import Any, Optional

import joblib

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
ARTIFACT_DIR = ROOT / "artifacts"
FRAUD_MODEL_PATH = ROOT / "fraud_model.pkl"
XGBOOST_MODEL_PATH = ROOT / "xgboost_fraud_model.joblib"
ANOMALY_MODEL_PATH = ROOT / "anomaly_model.pkl"
METADATA_PATH = ROOT / "feature_metadata.json"
EVALUATION_PATH = ROOT / "evaluation_results.json"

# Module-level cache so the model is loaded once per process
_xgboost_model: Optional[Any] = None


def load_fraud_model():
    """Loads the legacy fraud_model.pkl (used by the internal ml/ predict pipeline)."""
    if not FRAUD_MODEL_PATH.exists():
        raise FileNotFoundError(f"Fraud model not found: {FRAUD_MODEL_PATH}. Run training first.")
    return joblib.load(FRAUD_MODEL_PATH)


def load_xgboost_model() -> Any:
    """Loads (and caches) the trained XGBoost model from xgboost_fraud_model.joblib.

    Returns the loaded XGBoost classifier.  Raises FileNotFoundError if the
    model artefact is missing from the expected path.
    """
    global _xgboost_model
    if _xgboost_model is not None:
        return _xgboost_model
    if not XGBOOST_MODEL_PATH.exists():
        raise FileNotFoundError(
            f"XGBoost model not found at {XGBOOST_MODEL_PATH}. "
            "Ensure xgboost_fraud_model.joblib is present in app/ml/ml/."
        )
    _xgboost_model = joblib.load(XGBOOST_MODEL_PATH)
    return _xgboost_model
