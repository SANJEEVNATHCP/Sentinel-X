"""
FraudLens AI - UPI Transaction ORM Models
Stores parsed transactions and ML behavioral analysis results.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Integer, JSON
from app.database import Base

class TransactionBatch(Base):
    __tablename__ = "transaction_batches"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    investigation_id = Column(String(36), ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False, index=True)
    total_transactions = Column(Integer, default=0, nullable=False)
    user_historical_mean = Column(Float, default=0.0, nullable=False)
    user_historical_std = Column(Float, default=0.0, nullable=False)
    high_risk_count = Column(Integer, default=0, nullable=False)
    summary_json = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    batch_id = Column(String(36), ForeignKey("transaction_batches.id", ondelete="CASCADE"), nullable=False, index=True)
    transaction_id = Column(String(100), nullable=True)
    amount = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=True)
    sender = Column(String(255), nullable=True)
    receiver = Column(String(255), nullable=True)
    upi_id = Column(String(255), nullable=True)
    device_id = Column(String(100), nullable=True)
    location = Column(String(100), nullable=True)
    fraud_probability = Column(Float, default=0.0, nullable=False)
    anomaly_score = Column(Float, default=0.0, nullable=False)
    is_anomalous = Column(Integer, default=0, nullable=False)
