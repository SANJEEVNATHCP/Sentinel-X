"""
FraudLens AI - Company & Entity Verification Schemas
Supports authoritative dataset evaluation (Active vs Inactive) and LinkedIn presence.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class CompanyVerifyRequest(BaseModel):
    company_name: str = Field(..., min_length=2, description="Target company name or brand")
    domain: Optional[str] = Field(None, description="Company official domain or website")
    recruiter_email: Optional[str] = Field(None, description="Recruiter email address to verify against domain")

class CompanyVerifyResponse(BaseModel):
    searched_name: str
    mca_verified: bool
    company_name: Optional[str] = None
    cin: Optional[str] = None
    company_status: str # "Active", "Inactive", "NOT_FOUND"
    roc: Optional[str] = None
    registered_state: Optional[str] = None
    brand_name: Optional[str] = None
    official_domain: Optional[str] = None
    official_website: Optional[str] = None
    domain_match: Optional[bool] = None
    verification_source: str
    verification_note: Optional[str] = None
    risk_level: str # "LOW", "HIGH_RISK", "UNVERIFIED"
    investigation_id: Optional[str] = None
    id: Optional[str] = None


class LinkedInVerifyRequest(BaseModel):
    linkedin_url: str = Field(..., description="LinkedIn company URL, e.g. https://www.linkedin.com/company/example")

class LinkedInVerifyResponse(BaseModel):
    linkedin_found: bool
    company_name: Optional[str] = None
    linkedin_company_url: str
    company_slug: Optional[str] = None
    website_match: Optional[bool] = None
    confidence: float
    verification_status: str # "VERIFIED", "UNVERIFIED", "INVALID_FORMAT"
    verification_message: str

class TrustScoreResponse(BaseModel):
    company_name: str
    trust_score: float # 0 to 100
    risk_level: str # "TRUSTED", "MOSTLY_TRUSTED", "NEEDS_VERIFICATION", "SUSPICIOUS", "LIKELY_SCAM"
    components: Dict[str, Any]
    evidence: List[Dict[str, Any]]
    recommendations: List[str]
