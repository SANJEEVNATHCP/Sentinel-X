"""
FraudLens AI - Risk Factor ORM Model
Stores weighted risk factors that contributed to the final score.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base

class RiskFactor(Base):
    __tablename__ = "risk_factors"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    investigation_id = Column(String(36), ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    name = Column(String(150), nullable=False)
    weight = Column(Float, default=1.0, nullable=False)
    contribution = Column(Float, default=0.0, nullable=False)
    description = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    investigation = relationship("Investigation", back_populates="risk_factors")
