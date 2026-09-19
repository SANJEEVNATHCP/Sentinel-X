"""ML Service Integration Layer for FraudSentinel X.

This module acts as the integration contract between the FastAPI backend
and the ML / SHAP fraud detection model developed and owned by Person 1.

Expected Interface for Person 1 (ML & SHAP Module):
---------------------------------------------------
Person 1's module should expose or register a provider with:
1. predict(transaction_data: dict) -> dict:
   Expected return:
   {
       "transaction_id": str,
       "risk_score": float,      # 0 to 100
       "risk_level": str,       # "LOW", "MEDIUM", "HIGH"
       "anomaly_score": float,   # Isolation Forest anomaly score
       "risk_factors": list[str] # Key flags identified by the classifier
   }

2. explain(transaction_data: dict) -> dict:
   Expected return:
   {
       "transaction_id": str,
       "factors": [
           {"feature": str, "impact": float}  # SHAP feature contributions
       ]
   }
"""

import importlib
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger("fraudsentinel.ml_service")


class DevelopmentFallbackMLAdapter:
    """Fallback adapter used ONLY when Person 1's ML model is not yet connected.

    This ensures frontend integration can proceed during development without
    falsely fabricating or misrepresenting real ML / SHAP predictions.
    """

    def predict(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculates rule-based heuristic indicators as a development placeholder.

        Clearly flagged as 'development_fallback' so consumers know real ML is not active.
        """
        txn_id = transaction_data.get("transaction_id", "UNKNOWN")
        amount = float(transaction_data.get("amount", 0.0))
        is_new_device = bool(transaction_data.get("is_new_device", False))
        is_new_beneficiary = bool(transaction_data.get("is_new_beneficiary", False))

        # Check if an existing Alert was passed or already generated
        existing_alert = transaction_data.get("existing_alert")
        if existing_alert:
            return {
                "transaction_id": txn_id,
                "risk_score": float(existing_alert.risk_score),
                "risk_level": str(existing_alert.risk_level),
                "anomaly_score": 0.85 if existing_alert.risk_level == "HIGH" else 0.15,
                "risk_factors": [
                    "High amount deviation" if amount > 5000 else "Normal amount",
                    "Unrecognized device" if is_new_device else "Known device",
                    "New unverified beneficiary" if is_new_beneficiary else "Verified beneficiary",
                ],
                "model_status": "development_fallback (using stored prototype alert)",
            }

        # Basic heuristic calculation for dev testing
        risk_score = 15.0
        factors = []
        if amount > 10000:
            risk_score += 40.0
            factors.append("amount_deviation")
        if is_new_device:
            risk_score += 25.0
            factors.append("is_new_device")
        if is_new_beneficiary:
            risk_score += 20.0
            factors.append("is_new_beneficiary")

        risk_score = min(risk_score, 100.0)
        risk_level = "HIGH" if risk_score >= 75.0 else ("MEDIUM" if risk_score >= 40.0 else "LOW")

        return {
            "transaction_id": txn_id,
            "risk_score": round(risk_score, 2),
            "risk_level": risk_level,
            "anomaly_score": 0.75 if risk_level == "HIGH" else 0.15,
            "risk_factors": factors,
            "model_status": "development_fallback (Person 1 ML model pending connection)",
        }

    def explain(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Provides heuristic attributions for development testing.

        Does not pretend to be SHAP. Returns explicit dev indicator.
        """
        txn_id = transaction_data.get("transaction_id", "UNKNOWN")
        factors: List[Dict[str, Any]] = []

        if float(transaction_data.get("amount", 0.0)) > 5000:
            factors.append({"feature": "amount_deviation", "impact": 0.38})
        if transaction_data.get("is_new_device"):
            factors.append({"feature": "is_new_device", "impact": 0.28})
        if transaction_data.get("is_new_beneficiary"):
            factors.append({"feature": "is_new_beneficiary", "impact": 0.22})
        if transaction_data.get("location") not in [None, "", "Mumbai, IN"]:
            factors.append({"feature": "unusual_location", "impact": 0.12})

        return {
            "transaction_id": txn_id,
            "factors": factors,
            "model_status": "development_fallback (SHAP engine pending Person 1 integration)",
        }


# Model registry: allows Person 1 to inject or register their model dynamically
_active_ml_provider: Optional[Any] = None


def register_ml_provider(provider: Any):
    """Allows Person 1 to register their custom ML / SHAP provider at runtime."""
    global _active_ml_provider
    _active_ml_provider = provider
    logger.info("Custom ML provider successfully registered.")


def _get_provider():
    """Attempts to discover Person 1's real ML module, or falls back to development adapter."""
    global _active_ml_provider
    if _active_ml_provider is not None:
        return _active_ml_provider

    # Check for possible ML module implementations by Person 1
    candidates = ["ml.fraud_detector", "backend.ml.model", "services.ml_model"]
    for candidate in candidates:
        try:
            mod = importlib.import_module(candidate)
            if hasattr(mod, "predict") and hasattr(mod, "explain"):
                logger.info(f"Loaded real ML model from {candidate}")
                _active_ml_provider = mod
                return mod
        except (ImportError, AttributeError):
            continue

    # Return clearly separated development fallback
    return DevelopmentFallbackMLAdapter()


def predict_transaction(transaction_data: Dict[str, Any]) -> Dict[str, Any]:
    """Primary backend interface to predict fraud risk for a transaction.

    Returns:
        {
            "transaction_id": str,
            "risk_score": float,
            "risk_level": str,
            "anomaly_score": float,
            "risk_factors": list[str],
            "model_status": str
        }
    """
    provider = _get_provider()
    try:
        result = provider.predict(transaction_data)
        # Ensure all required keys exist
        return {
            "transaction_id": str(result.get("transaction_id", transaction_data.get("transaction_id", ""))),
            "risk_score": float(result.get("risk_score", 0.0)),
            "risk_level": str(result.get("risk_level", "LOW")),
            "anomaly_score": float(result.get("anomaly_score", 0.0)),
            "risk_factors": list(result.get("risk_factors", [])),
            "model_status": result.get("model_status", "active"),
        }
    except Exception as e:
        logger.error(f"Error invoking ML predict service: {e}", exc_info=True)
        raise RuntimeError(f"ML prediction failed: {str(e)}")


def explain_transaction(transaction_data: Dict[str, Any]) -> Dict[str, Any]:
    """Primary backend interface to get SHAP / feature explanation for a transaction.

    Returns:
        {
            "transaction_id": str,
            "factors": [
                {"feature": str, "impact": float}
            ],
            "model_status": str
        }
    """
    provider = _get_provider()
    try:
        result = provider.explain(transaction_data)
        return {
            "transaction_id": str(result.get("transaction_id", transaction_data.get("transaction_id", ""))),
            "factors": result.get("factors", []),
            "model_status": result.get("model_status", "active"),
        }
    except Exception as e:
        logger.error(f"Error invoking SHAP explanation service: {e}", exc_info=True)
        raise RuntimeError(f"SHAP explanation failed: {str(e)}")
