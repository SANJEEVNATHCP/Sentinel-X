"""
FraudLens AI - Scam Analysis & Spam URL Dataset ORM Models
Stores indexed spam/threat URLs (ACTIVE / INACTIVE) and multi-signal scam checks.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text, Boolean, JSON
from app.database import Base

class SpamURL(Base):
    """
    Local threat feed dataset table (imported from spam_urls.csv).
    Identifies if a URL exists in the known dataset and its status (ACTIVE / INACTIVE).
    """
    __tablename__ = "spam_urls"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    url = Column(String(1000), nullable=False)
    normalized_url = Column(String(1000), nullable=False, index=True)
    domain = Column(String(255), nullable=False, index=True)
    status = Column(String(50), nullable=False, index=True) # "ACTIVE", "INACTIVE"
    source = Column(String(100), default="FraudLens URL Dataset", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class ScamAnalysis(Base):
    """Stores URL, screenshot, or conversational scam analysis sessions."""
    __tablename__ = "scam_analyses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    investigation_id = Column(String(36), ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    target_url = Column(String(1000), nullable=True)
    domain = Column(String(255), nullable=True)
    dataset_found = Column(Boolean, default=False, nullable=False)
    dataset_status = Column(String(50), nullable=True) # "ACTIVE", "INACTIVE", "NOT_FOUND"
    
    virustotal_status = Column(String(50), default="UNAVAILABLE", nullable=False)
    virustotal_malicious = Column(Float, default=0, nullable=False)
    virustotal_suspicious = Column(Float, default=0, nullable=False)
    
    attack_patterns = Column(JSON, nullable=False, default=list)
    signals_json = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
