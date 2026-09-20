"""
FraudLens AI - Investigation Result ORM Model
Persistent derived analysis result. Survives End-Task raw data scrubbing.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class InvestigationResult(Base):
    __tablename__ = "investigation_results"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    investigation_id = Column(String(36), ForeignKey("investigations.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    type = Column(String(50), nullable=False)
    risk_score = Column(Float, nullable=False)
    risk_level = Column(String(50), nullable=False)
    summary = Column(Text, nullable=False)
    recommendation = Column(Text, nullable=False)
    
    # Structured JSON payloads preserved for audit and reports
    evidence_json = Column(JSON, nullable=False, default=list)
    risk_factors_json = Column(JSON, nullable=False, default=list)
    verification_json = Column(JSON, nullable=False, default=dict)
    attack_patterns_json = Column(JSON, nullable=False, default=list)
    transactions_json = Column(JSON, nullable=True, default=list)  # Per-transaction XGBoost scores
    
    ai_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="results")
    investigation = relationship("Investigation", back_populates="result")
