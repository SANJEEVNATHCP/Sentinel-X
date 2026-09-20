"""
FraudLens AI - Behavioral Anomaly Detection Service
Applies IsolationForest unsupervised anomaly detection to flag deviant transaction profiles.
"""

import os
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, List
from app.config import settings
from app.logging_config import logger

class AnomalyService:
    _model = None
    _model_path = os.path.join(settings.MODELS_DIR, "anomaly_model.pkl")

    @classmethod
    def get_model(cls):
        if cls._model is None:
            # Check models directory first, then app/ml/ml as fallback
            search_paths = [
                cls._model_path,
                os.path.join(os.path.dirname(__file__), "..", "ml", "ml", "anomaly_model.pkl")
            ]
            for p in search_paths:
                if os.path.exists(p):
                    try:
                        cls._model = joblib.load(p)
                        logger.info(f"Loaded Isolation Forest model from {p}")
                        break
                    except Exception as e:
                        logger.warning(f"Failed to load model from {p}: {e}")
        return cls._model

    @classmethod
    def detect_anomaly(cls, features: Dict[str, float]) -> Dict[str, Any]:
        """
        Runs the Isolation Forest ('isolate frost') ML model.
        Returns anomaly_score (0.0 to 1.0) and is_anomalous binary flag (1 for anomaly, 0 for normal).
        """
        model = cls.get_model()
        if model is not None:
            try:
                # Prepare expected 6 features matching training pipeline:
                # ['amount', 'amount_deviation', 'transaction_hour', 'transactions_previous_hour', 'location_deviation', 'beneficiary_count']
                amt = float(features.get("amount", 0.0))
                amt_dev = float(features.get("amount_deviation", features.get("amount_ratio", 1.0)))
                txn_hour = float(features.get("transaction_hour", features.get("hour", 12.0)))
                velocity = float(features.get("transactions_previous_hour", features.get("frequency", 1.0)))
                loc_dev = float(features.get("location_deviation", 0.0))
                ben_count = float(features.get("beneficiary_count", features.get("frequency", 1.0)))

                feat_dict = {
                    "amount": [amt],
                    "amount_deviation": [amt_dev],
                    "transaction_hour": [txn_hour],
                    "transactions_previous_hour": [velocity],
                    "location_deviation": [loc_dev],
                    "beneficiary_count": [ben_count]
                }

                if hasattr(model, "feature_names_in_"):
                    # Use exact feature names if available
                    cols = list(model.feature_names_in_)
                    row_data = {c: feat_dict.get(c, [0.0]) for c in cols}
                    input_df = pd.DataFrame(row_data)
                    pred = int(model.predict(input_df)[0])
                    dec_score = float(model.decision_function(input_df)[0])
                else:
                    vec = np.array([[amt, amt_dev, txn_hour, velocity, loc_dev, ben_count]])
                    pred = int(model.predict(vec)[0])
                    dec_score = float(model.decision_function(vec)[0])

                # Decision function: positive for normal (> 0.0), negative for outliers (< 0.0).
                # Transform to 0.0 - 1.0 anomaly scale
                normalized_score = float(np.clip(0.5 - (dec_score * 2.5), 0.0, 1.0))
                is_anom = 1 if pred == -1 or normalized_score >= 0.65 else 0

                return {
                    "anomaly_score": round(normalized_score, 4),
                    "is_anomalous": is_anom,
                    "model": "Isolation Forest"
                }
            except Exception as e:
                logger.warning(f"Isolation Forest inference error: {e}")

        # Fallback heuristic if model cannot be evaluated
        ratio = features.get("amount_ratio", features.get("amount_deviation", 1.0))
        is_night = features.get("is_night_txn", 0)
        freq = features.get("frequency", 1)

        is_anom = 1 if (ratio > 4.5 or (ratio > 2.5 and is_night) or freq >= 4) else 0
        score = min(0.95, (ratio / 10.0) * 0.6 + (0.2 if is_night else 0.0) + (0.15 if freq >= 3 else 0.0))
        return {
            "anomaly_score": round(score, 4),
            "is_anomalous": is_anom,
            "model": "Isolation Forest (Heuristic fallback)"
        }
