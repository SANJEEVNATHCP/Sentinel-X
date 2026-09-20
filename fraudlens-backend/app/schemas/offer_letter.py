"""
FraudLens AI - Offer Letter Verification Schemas
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class OfferLetterExtractedData(BaseModel):
    company_name: Optional[str] = None
    company_website: Optional[str] = None
    recruiter_name: Optional[str] = None
    recruiter_email: Optional[str] = None
    job_role: Optional[str] = None
    salary: Optional[str] = None
    offer_date: Optional[str] = None
    phone_number: Optional[str] = None
    location: Optional[str] = None
    hr_contact: Optional[str] = None

class OfferLetterResponse(BaseModel):
    investigation_id: str
    extracted_data: OfferLetterExtractedData
    mca_match_status: str # "Active", "Inactive", "NOT_FOUND"
    trust_score: float
    risk_level: str
    attack_patterns: List[Dict[str, Any]]
    evidence: List[Dict[str, Any]]
    risk_factors: List[Dict[str, Any]]
    recommendations: List[str]
    ai_summary: Optional[str] = None
    created_at: str
