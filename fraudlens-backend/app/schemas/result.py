"""
FraudLens AI - Results History & Report Schemas
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

class ResultListItem(BaseModel):
    id: str
    investigation_id: str
    type: str
    risk_score: float
    risk_level: str
    summary: str
    created_at: datetime

    class Config:
        from_attributes = True

class InvestigationResultDetail(BaseModel):
    id: str
    investigation_id: str
    type: str
    risk_score: float
    risk_level: str
    summary: str
    recommendation: str
    evidence: List[Dict[str, Any]]
    risk_factors: List[Dict[str, Any]]
    verification: Dict[str, Any]
    attack_patterns: List[Dict[str, Any]]
    ai_summary: Optional[str] = None
    created_at: datetime
    download_pdf_url: str
    download_json_url: str

class ResultFilterParams(BaseModel):
    type: Optional[str] = None
    risk_level: Optional[str] = None
    search: Optional[str] = None
