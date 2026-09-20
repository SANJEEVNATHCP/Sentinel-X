"""SHAP explanations for the XGBoost classifier."""

from __future__ import annotations

from typing import Any

import numpy as np

EXPLANATIONS = {
    "amount": "Transaction amount is high in absolute terms.",
    "amount_deviation": "Transaction amount is significantly higher than the historical average.",
    "is_new_device": "Transaction originated from a device not previously associated with the user's activity.",
    "is_new_beneficiary": "Beneficiary has not previously appeared in the user's transaction history.",
    "transaction_hour": "Transaction occurred during an unusual time period.",
    "transactions_previous_hour": "Transaction velocity is higher than the observed baseline.",
    "location_deviation": "Transaction location differs significantly from the user's normal region.",
    "previous_fraud_alerts": "The user has previous fraud alerts in the observed history.",
    "beneficiary_count": "Beneficiary activity differs from the observed pattern.",
}


def explain_prediction(model: Any, features, top_n: int = 5) -> list[dict[str, Any]]:
    try:
        import shap
        values = shap.TreeExplainer(model)(features)
        shap_values = values.values
        if shap_values.ndim == 3:
            shap_values = shap_values[:, :, 1]
        row = np.asarray(shap_values[0], dtype=float)
    except Exception as exc:
        raise RuntimeError("SHAP explanation could not be generated") from exc
    names = list(features.columns)
    ranked = sorted(zip(names, row), key=lambda item: abs(item[1]), reverse=True)[:top_n]
    result = []
    for name, contribution in ranked:
        value = features.iloc[0][name]
        result.append({
            "feature": name,
            "value": float(value),
            "contribution": round(float(contribution), 6),
            "direction": "increases_risk" if contribution >= 0 else "decreases_risk",
            "explanation": EXPLANATIONS.get(name, "This feature contributed to the model decision."),
        })
    return result


def get_risk_factors(model: Any, features, top_n: int = 5) -> list[dict[str, Any]]:
    return explain_prediction(model, features, top_n=top_n)
