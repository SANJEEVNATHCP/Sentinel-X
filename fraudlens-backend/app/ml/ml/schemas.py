"""Typed integration schemas for FraudSentinel X."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class TransactionInput(BaseModel):
    model_config = ConfigDict(extra="allow")

    transaction_id: str
    amount: float = Field(gt=0)
    timestamp: Any
    user_id: str | None = None
    device_id: str | None = None
    beneficiary_id: str | None = None
    location_region: str | None = None
    transaction_frequency: float = 0
    avg_amount: float = 0
    is_new_device: bool = False
    is_new_beneficiary: bool = False
    location_deviation: float = 0
    transactions_previous_hour: float = 0
    beneficiary_count: float = 0
    previous_fraud_alerts: float = 0


class RiskFactor(BaseModel):
    feature: str
    value: float | int | str | bool | None
    contribution: float
    direction: str
    explanation: str


class AnomalyResult(BaseModel):
    anomaly_score: float = Field(ge=0, le=1)
    is_anomalous: bool


class ModelExplanation(BaseModel):
    factors: list[RiskFactor]
    base_value: float | None = None


class PredictionResult(BaseModel):
    transaction_id: str
    risk_score: int = Field(ge=0, le=100)
    risk_level: str
    anomaly_score: float = Field(ge=0, le=1)
    is_anomalous: bool
    model_signal: float = Field(ge=0, le=1)
    top_risk_factors: list[RiskFactor]
    model: str = "XGBoost"
    anomaly_model: str = "Isolation Forest"
    explanation_method: str = "SHAP"
    processed_features: dict[str, float]


class EvaluationResult(BaseModel):
    precision: float
    recall: float
    f1_score: float
    pr_auc: float
    false_positive_rate: float
    confusion_matrix: list[list[int]]
