"""Public prediction API for the FastAPI integration layer."""

from __future__ import annotations

from typing import Any

import pandas as pd

from .anomaly import load_anomaly_model, score_anomalies
from .features import engineer_features
from .model_utils import ANOMALY_MODEL_PATH, load_fraud_model
from .risk_score import calculate_risk_score
from .schemas import PredictionResult
from .shap_explainer import explain_prediction
from .validation import require_valid_transactions


def _as_frame(transaction: Any) -> pd.DataFrame:
    if isinstance(transaction, pd.DataFrame):
        return transaction.copy()
    if hasattr(transaction, "model_dump"):
        transaction = transaction.model_dump()
    elif hasattr(transaction, "dict"):
        transaction = transaction.dict()
    if not isinstance(transaction, dict):
        raise TypeError("Transaction must be a mapping, Pydantic model, or DataFrame")
    return pd.DataFrame([transaction])


def predict_dataframe(dataframe: pd.DataFrame) -> list[dict[str, Any]]:
    require_valid_transactions(dataframe)
    model = load_fraud_model()
    anomaly_model = load_anomaly_model(ANOMALY_MODEL_PATH)
    processed = engineer_features(dataframe)
    model_signal = model.predict_proba(processed)[:, 1]
    anomaly_scores, anomalous = score_anomalies(anomaly_model, processed)
    results: list[dict[str, Any]] = []
    for index, row in processed.iterrows():
        row_features = processed.iloc[[index]]
        factors = explain_prediction(model, row_features)
        risk = calculate_risk_score(float(model_signal[index]), float(anomaly_scores[index]), row.to_dict())
        result = PredictionResult(
            transaction_id=str(dataframe.iloc[index]["transaction_id"]),
            risk_score=int(risk["risk_score"]), risk_level=str(risk["risk_level"]),
            anomaly_score=round(float(anomaly_scores[index]), 6), is_anomalous=bool(anomalous[index]),
            model_signal=round(float(model_signal[index]), 6), top_risk_factors=factors,
            processed_features={key: round(float(value), 6) for key, value in row.to_dict().items()},
        )
        results.append(result.model_dump())
    return results


def predict_transaction(transaction: Any) -> dict[str, Any]:
    return predict_dataframe(_as_frame(transaction))[0]


def get_model_explanation(transaction: Any) -> list[dict[str, Any]]:
    return predict_transaction(transaction)["top_risk_factors"]


def get_risk_factors(transaction: Any) -> list[dict[str, Any]]:
    return get_model_explanation(transaction)


def get_model_working(transaction: Any) -> dict[str, Any]:
    prediction = predict_transaction(transaction)
    return {
        "pipeline": ["Input Data", "Feature Engineering", "XGBoost Fraud Model", "Isolation Forest", "Risk Scoring", "SHAP Explanation", "Fraud Result"],
        "input_features": list(_as_frame(transaction).columns),
        "processed_features": prediction["processed_features"], "model_name": "XGBoost",
        "anomaly_model": "Isolation Forest", "risk_score": prediction["risk_score"],
        "risk_level": prediction["risk_level"], "top_features": prediction["top_risk_factors"],
    }
