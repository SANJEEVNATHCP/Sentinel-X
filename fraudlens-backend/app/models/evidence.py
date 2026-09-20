"""
FraudLens AI - Evidence ORM Model
Stores granular, explainable signals with observable values and confidence ratings.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base

class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    investigation_id = Column(String(36), ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    category = Column(String(100), nullable=False) # e.g. "Transaction Behavior", "Domain Reputation", "Entity Legitimacy"
    signal = Column(String(150), nullable=False)   # e.g. "Amount Anomaly", "Inactive Company Registry"
    observed_value = Column(String(255), nullable=True) # e.g. "₹48,500"
    reference_value = Column(String(255), nullable=True)# e.g. "User average ₹1,850"
    severity = Column(String(50), nullable=False)       # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    confidence = Column(Float, default=1.0, nullable=False) # 0.0 to 1.0
    risk_contribution = Column(Float, default=0.0, nullable=False) # Points added to score
    source = Column(String(100), nullable=False)        # e.g. "Behavioral Engine", "MCA Registry Dataset"
    explanation = Column(Text, nullable=False)          # Human-readable auditable description
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    investigation = relationship("Investigation", back_populates="evidence_items")
