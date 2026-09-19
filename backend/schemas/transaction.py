from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    transaction_id: str = Field(..., description="Unique transaction identifier")
    user_id: str = Field(..., description="Identifier of the transacting user")
    amount: float = Field(..., description="Transaction amount")
    timestamp: datetime = Field(..., description="Timestamp of transaction")
    device_id: str = Field(..., description="Device ID used for the transaction")
    beneficiary_id: str = Field(..., description="Recipient / beneficiary ID")
    location: str = Field(..., description="Geographic or IP location of transaction")
    is_new_device: bool = Field(..., description="Whether device is newly observed for user")
    is_new_beneficiary: bool = Field(..., description="Whether beneficiary is newly observed for user")


class RiskResponse(BaseModel):
    transaction_id: str
    risk_score: float = Field(..., description="Calculated risk score (0-100)")
    risk_level: str = Field(..., description="Categorical risk level (LOW, MEDIUM, HIGH)")
    anomaly_score: float = Field(..., description="Isolation Forest anomaly score")
    model_status: Optional[str] = Field(None, description="Status of ML model (e.g. active, fallback)")


class FactorItem(BaseModel):
    feature: str = Field(..., description="Name of the feature influencing the prediction")
    impact: float = Field(..., description="SHAP feature attribution impact value")


class ExplanationResponse(BaseModel):
    transaction_id: str
    factors: List[FactorItem] = Field(default_factory=list, description="List of top feature attributions")
    model_status: Optional[str] = Field(None, description="Status of explanation engine")
