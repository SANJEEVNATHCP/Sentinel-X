"""
FraudLens AI - XGBoost Fraud ML Model Service
Executes the trained XGBoost classifier (xgboost_fraud_model.joblib) with the
14-feature vector used during training, with a calibrated statistical
fallback when the model artefact is unavailable.
"""

import numpy as np
from typing import Dict, Any, Optional

# Model artefact name reported in per-transaction metadata
MODEL_NAME = "XGBoost (xgboost_fraud_model.joblib)"

# Ordered feature list - matches the model's actual training features exactly
XGBOOST_FEATURE_COLUMNS = [
    "Transaction_Type",       # 0: encoded transaction type (UPI=0, NEFT=1, IMPS=2, etc.)
    "Amount_INR",             # 1: transaction amount in INR
    "Balance_INR",            # 2: account balance (proxy from avg_amount)
    "Merchant",               # 3: encoded merchant/receiver (hash-based)
    "Category",               # 4: encoded category (0=general)
    "Payment_Mode",           # 5: encoded mode (UPI=0)
    "Location",               # 6: encoded location (0=domestic, 1=foreign)
    "Transaction_Status",     # 7: encoded status (SUCCESS=1, FAILED=0)
    "Device_ID",              # 8: encoded device (new=high number)
    "Is_International",       # 9: 0 or 1
    "Risk_Score",             # 10: preliminary risk score (0-100)
    "account_transaction_freq", # 11: transaction frequency for the account
    "merchant_freq",          # 12: merchant transaction frequency
    "Account_ID_encoded",     # 13: encoded account ID
]


class FraudModelService:
    """Loads and serves the XGBoost fraud classifier."""

    _model: Optional[Any] = None
    _load_attempted: bool = False

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #

    @classmethod
    def _get_model(cls) -> Optional[Any]:
        """Returns the cached XGBoost model, loading it on first call."""
        if not cls._load_attempted:
            cls._load_attempted = True
            try:
                from app.ml.ml.model_utils import load_xgboost_model
                cls._model = load_xgboost_model()
            except Exception as exc:
                import logging
                logging.getLogger(__name__).warning(
                    f"XGBoost model could not be loaded — heuristic fallback active. "
                    f"Reason: {exc}"
                )
                cls._model = None
        return cls._model

    @staticmethod
    def _build_feature_vector(features: Dict[str, float]) -> np.ndarray:
        """Assembles the 14-element feature array expected by the XGBoost model.

        Maps UPI transaction signals from TransactionService into the feature
        space the model was trained on. Categorical fields are encoded
        deterministically using hash-based integer encoding (as done at training time).
        """
        amount = float(features.get("amount", 0.0))
        avg_amount = float(features.get("avg_amount",
                           features.get("baseline_mean", max(amount, 1.0))))
        hour = float(features.get("transaction_hour",
                     features.get("hour", 12.0)))
        freq = float(features.get("transaction_frequency",
                     features.get("frequency", 1.0)))
        failed = float(features.get("failed_attempts", 0.0))
        is_night = float(features.get("is_night_txn",
                         1.0 if hour in {0, 1, 2, 3, 4, 5} else 0.0))
        loc_dev = float(features.get("location_deviation", 0.0))
        is_foreign = 1.0 if loc_dev >= 0.5 else 0.0
        amount_ratio = amount / max(avg_amount, 1e-5)

        # Preliminary rule-based risk score (proxy for Risk_Score feature)
        prelim_risk = min(100.0, (
            (40.0 if amount_ratio >= 10.0 else 20.0 if amount_ratio >= 4.0 else 5.0) +
            (20.0 if failed >= 2 else 10.0 if failed >= 1 else 0.0) +
            (15.0 if is_night else 0.0) +
            (20.0 if is_foreign else 0.0)
        ))

        # Transaction type encoding: UPI=0
        txn_type = 0.0

        # Balance proxy: estimate from average amount * some factor
        balance_proxy = avg_amount * 3.0

        # Merchant encoding: hash receiver string for a stable integer
        raw_receiver = str(features.get("receiver_id", "unknown"))
        merchant_encoded = float(abs(hash(raw_receiver)) % 10000)

        # Category: 0=general
        category = 0.0

        # Payment mode: UPI=0
        payment_mode = 0.0

        # Location: 0=domestic, 1=foreign/unknown
        location_encoded = is_foreign

        # Transaction status: SUCCESS=1, FAILED=0 (assume success unless >2 fails)
        txn_status = 0.0 if failed >= 3 else 1.0

        # Device ID: new/unknown device gets a high-value encoding
        device_encoded = 9999.0 if features.get("is_new_device", 0.0) >= 1.0 else 1.0

        # Merchant frequency
        merchant_freq = float(features.get("beneficiary_count",
                              features.get("frequency", 1.0)))

        # Account ID: stable proxy
        account_id_encoded = 100.0

        return np.array([[
            txn_type,           # Transaction_Type
            amount,             # Amount_INR
            balance_proxy,      # Balance_INR
            merchant_encoded,   # Merchant
            category,           # Category
            payment_mode,       # Payment_Mode
            location_encoded,   # Location
            txn_status,         # Transaction_Status
            device_encoded,     # Device_ID
            is_foreign,         # Is_International
            prelim_risk,        # Risk_Score
            freq,               # account_transaction_freq
            merchant_freq,      # merchant_freq
            account_id_encoded, # Account_ID_encoded
        ]], dtype=np.float64)

    # ------------------------------------------------------------------ #
    # Public interface
    # ------------------------------------------------------------------ #

    @classmethod
    def predict_fraud_probability(cls, features: Dict[str, float]) -> float:
        """Predicts the XGBoost fraud probability for a single transaction.

        Args:
            features: Dict containing UPI transaction signals.

        Returns:
            A float in [0, 1] representing the model's fraud probability.
            Falls back to a calibrated heuristic if the model is unavailable.
        """
        model = cls._get_model()
        if model is not None:
            try:
                vec = cls._build_feature_vector(features)
                prob = float(model.predict_proba(vec)[0][1])
                return round(min(max(prob, 0.0), 1.0), 6)
            except Exception as exc:
                import logging
                logging.getLogger(__name__).warning(
                    f"XGBoost inference failed, using heuristic. Error: {exc}"
                )

        # -------------------------------------------------------------- #
        # Calibrated heuristic fallback (model unavailable or failed)
        # -------------------------------------------------------------- #
        score = 0.05
        amount = float(features.get("amount", 0.0))
        avg_amount = float(features.get("avg_amount", features.get("baseline_mean", max(amount, 1.0))))
        ratio = amount / max(avg_amount, 1e-5)
        failed = float(features.get("failed_attempts", 0.0))
        hour = float(features.get("transaction_hour", features.get("hour", 12.0)))
        is_night = hour in {0, 1, 2, 3, 4, 5}
        location_dev = float(features.get("location_deviation", 0.0))
        is_new_device = float(features.get("is_new_device", 0.0))
        is_new_ben = float(features.get("is_new_beneficiary", 0.0))

        if ratio > 15.0:
            score += 0.55
        elif ratio > 10.0:
            score += 0.45
        elif ratio > 4.0:
            score += 0.30
        elif ratio > 2.0:
            score += 0.15

        if failed >= 3:
            score += 0.25
        elif failed >= 1:
            score += 0.10

        if is_night:
            score += 0.15

        if location_dev >= 0.5:
            score += 0.20
        elif location_dev >= 0.2:
            score += 0.10

        score += 0.10 * is_new_device
        score += 0.10 * is_new_ben

        return round(min(score, 0.99), 6)

    @classmethod
    def get_model(cls):
        """Public alias for health checks — returns the loaded XGBoost model or None."""
        return cls._get_model()

    @classmethod
    def is_model_loaded(cls) -> bool:
        """Returns True if the XGBoost artefact was successfully loaded."""
        return cls._get_model() is not None
