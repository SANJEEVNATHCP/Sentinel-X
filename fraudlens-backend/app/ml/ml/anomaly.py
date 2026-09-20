"""Isolation Forest behavior model and documented score normalization."""

from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import IsolationForest

ANOMALY_FEATURES = ["amount", "amount_deviation", "transaction_hour", "transactions_previous_hour", "location_deviation", "beneficiary_count"]


def train_anomaly_model(features, path: Path) -> IsolationForest:
    model = IsolationForest(n_estimators=150, contamination=0.08, random_state=42)
    model.fit(features[ANOMALY_FEATURES])
    joblib.dump(model, path)
    return model


def load_anomaly_model(path: Path) -> IsolationForest:
    if not path.exists():
        raise FileNotFoundError(f"Anomaly model not found: {path}. Run training first.")
    return joblib.load(path)


def score_anomalies(model: IsolationForest, features) -> tuple[np.ndarray, np.ndarray]:
    raw = model.score_samples(features[ANOMALY_FEATURES])
    # Isolation Forest scores are unbounded-ish negative values, not probabilities.
    # This monotonic transform maps the observed score distribution to [0, 1].
    anomaly_score = np.clip(0.5 - raw, 0.0, 1.0)
    is_anomalous = model.predict(features[ANOMALY_FEATURES]) == -1
    return anomaly_score, is_anomalous
