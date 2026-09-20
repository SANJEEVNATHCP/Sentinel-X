"""
FraudLens AI - UPI Transaction Analysis Schemas
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class TransactionRow(BaseModel):
    transaction_id: Optional[str] = None
    amount: float
    timestamp: Optional[str] = None
    sender: Optional[str] = None
    receiver: Optional[str] = None
    receiver_id: Optional[str] = None
    upi_id: Optional[str] = None
    device_id: Optional[str] = None
    location: Optional[str] = None
    frequency: int = 1
    baseline_mean: float = 0.0
    amount_ratio: float = 1.0
    what_went_wrong: Optional[str] = None
    model_used: str = "Isolation Forest"
    xgboost_score: Optional[float] = None
    fraud_probability: float = 0.0
    anomaly_score: float = 0.0
    is_anomalous: int = 0
    signals: List[str] = []

class UPIAnalysisResponse(BaseModel):
    investigation_id: str
    total_transactions: int
    user_historical_mean: float
    user_historical_std: float
    high_risk_count: int
    risk_score: float
    risk_level: str
    summary: str
    evidence: List[Dict[str, Any]]
    risk_factors: List[Dict[str, Any]]
    recommendations: List[str]
    ai_summary: Optional[str] = None
    created_at: str
    transactions: List[TransactionRow]
