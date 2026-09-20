"""
FraudLens AI - Company & Verification ORM Models
Stores authoritative Company Master records (Active vs Inactive) and verification sessions.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text, Boolean, JSON
from app.database import Base

class Company(Base):
    """
    Authoritative Company Master Record imported from sample.xlsx / companies.csv.
    Identifies whether a corporate entity is Active (real) or Inactive (fake/defunct).
    """
    __tablename__ = "companies"

    cin = Column(String(100), primary_key=True, index=True)
    company_name = Column(String(255), nullable=False, index=True)
    normalized_name = Column(String(255), nullable=False, index=True)
    company_status = Column(String(50), nullable=False, index=True) # "Active", "Inactive"
    company_class = Column(String(100), nullable=True)
    company_category = Column(String(100), nullable=True)
    registered_state = Column(String(100), nullable=True)
    registrar_of_companies = Column(String(150), nullable=True)
    date_of_registration = Column(String(50), nullable=True)
    brand_name = Column(String(150), nullable=True, index=True)
    official_domain = Column(String(150), nullable=True, index=True)
    official_website = Column(String(255), nullable=True)
    domain_status = Column(String(100), nullable=True)
    domain_match_type = Column(String(100), nullable=True)
    primary_authority = Column(String(255), nullable=True)
    reference_dataset = Column(String(255), nullable=True)
    verification_note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class CompanyCheck(Base):
    """Stores the specific verification outcome for a company within an investigation."""
    __tablename__ = "company_checks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    investigation_id = Column(String(36), ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    searched_name = Column(String(255), nullable=False)
    mca_verified = Column(Boolean, default=False, nullable=False)
    company_status = Column(String(50), nullable=True) # "Active", "Inactive", "NOT_FOUND"
    cin = Column(String(100), nullable=True)
    roc = Column(String(150), nullable=True)
    
    linkedin_found = Column(Boolean, default=False, nullable=False)
    linkedin_status = Column(String(50), default="UNVERIFIED", nullable=False)
    website_verified = Column(Boolean, default=False, nullable=False)
    recruiter_verified = Column(Boolean, default=False, nullable=False)
    trust_score = Column(Float, default=0.0, nullable=False)
    
    details_json = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
