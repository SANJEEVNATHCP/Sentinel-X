"""
FraudLens AI - Offer Letter Verification ORM Model
Stores derived extraction and risk indicators from employment documents.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, JSON
from app.database import Base

class OfferLetterVerification(Base):
    __tablename__ = "offer_letter_verifications"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    investigation_id = Column(String(36), ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    company_name = Column(String(255), nullable=True)
    company_website = Column(String(255), nullable=True)
    recruiter_name = Column(String(255), nullable=True)
    recruiter_email = Column(String(255), nullable=True)
    job_role = Column(String(255), nullable=True)
    salary = Column(String(100), nullable=True)
    
    mca_match_status = Column(String(50), nullable=True)
    trust_score = Column(Float, default=0.0, nullable=False)
    
    extracted_fields = Column(JSON, nullable=False, default=dict)
    indicators = Column(JSON, nullable=False, default=list)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
