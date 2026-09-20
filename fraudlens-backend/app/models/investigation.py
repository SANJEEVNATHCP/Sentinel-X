"""
FraudLens AI - Investigation ORM Model
Tracks life-cycle states, risk classifications, and completion status.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base

class Investigation(Base):
    __tablename__ = "investigations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Types: UPI, SCAM_URL, COMPANY, PROFILE, IMAGE_CHAT, OFFER_LETTER
    type = Column(String(50), nullable=False, index=True)
    
    # Status: PENDING, PROCESSING, COMPLETED, FAILED, ENDED
    status = Column(String(50), default="PENDING", nullable=False, index=True)
    
    risk_score = Column(Float, default=0.0, nullable=False)
    # Risk Levels: LOW, MODERATE, SUSPICIOUS, HIGH_RISK
    risk_level = Column(String(50), default="LOW", nullable=False)
    
    summary = Column(Text, nullable=True)
    target_entity = Column(String(255), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="investigations")
    evidence_items = relationship("Evidence", back_populates="investigation", cascade="all, delete-orphan")
    risk_factors = relationship("RiskFactor", back_populates="investigation", cascade="all, delete-orphan")
    result = relationship("InvestigationResult", back_populates="investigation", uselist=False)
    uploaded_files = relationship("UploadedFile", back_populates="investigation", cascade="all, delete-orphan")
