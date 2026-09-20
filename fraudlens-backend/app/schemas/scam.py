"""
FraudLens AI - Scam & URL Intelligence Schemas
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class URLCheckRequest(BaseModel):
    url: str = Field(..., description="Target URL to analyze for security threats")

class LocalDatasetResult(BaseModel):
    dataset_found: bool
    status: str # "ACTIVE", "INACTIVE", "NOT_FOUND"
    source: str = "FraudLens URL Dataset"

class VirusTotalResult(BaseModel):
    scan_status: str # "COMPLETED", "UNAVAILABLE", "QUEUED"
    malicious: int = 0
    suspicious: int = 0
    harmless: int = 0
    undetected: int = 0
    reputation: int = 0

class URLCheckResponse(BaseModel):
    url: str
    normalized_url: str
    domain: str
    local_dataset: LocalDatasetResult
    virustotal: VirusTotalResult
    risk_score: float
    risk_level: str
    is_https: bool
    suspicious_patterns_detected: List[str]
    evidence: List[Dict[str, Any]]
    recommendations: List[str]
    investigation_id: Optional[str] = None
    id: Optional[str] = None

class ScamAnalyzeRequest(BaseModel):
    url: Optional[str] = None
    company_name: Optional[str] = None
    linkedin_url: Optional[str] = None
    recruiter_email: Optional[str] = None
    message_text: Optional[str] = None

class ScamAnalysisResponse(BaseModel):
    investigation_id: str
    type: str = "SCAM_URL"
    risk_score: float
    risk_level: str
    summary: str
    attack_patterns: List[Dict[str, Any]]
    evidence: List[Dict[str, Any]]
    risk_factors: List[Dict[str, Any]]
    recommendations: List[str]
    ai_summary: Optional[str] = None
    created_at: str
