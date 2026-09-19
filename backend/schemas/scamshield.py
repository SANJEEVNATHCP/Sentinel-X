from typing import List, Optional
from pydantic import BaseModel, Field


class URLAnalyzeRequest(BaseModel):
    url: str = Field(..., min_length=3, description="Target URL to inspect for fraud, phishing, or scam indicators")


class URLAnalyzeResponse(BaseModel):
    url: str
    risk_score: float = Field(..., description="Threat intelligence risk score (0-100)")
    risk_level: str = Field(..., description="Risk tier: Low, Medium, High, or Unknown")
    indicators: List[str] = Field(default_factory=list, description="Specific threat indicators detected")
    status: Optional[str] = Field(None, description="External verification status or message")
    provider: Optional[str] = Field(None, description="Active threat intelligence provider")
