"""
FraudLens AI - Investigation & What-If Engine Schemas
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class InvestigationResponse(BaseModel):
    id: str
    user_id: str
    type: str
    status: str
    risk_score: float
    risk_level: str
    summary: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class WhatIfSignalToggle(BaseModel):
    signal_id: Optional[str] = None
    signal_name: str
    enabled: bool

class WhatIfRequest(BaseModel):
    toggled_signals: List[WhatIfSignalToggle] = Field(
        default=[],
        description="List of risk signals to artificially enable or disable"
    )

class WhatIfResponse(BaseModel):
    investigation_id: str
    original_score: float
    scenario_score: float
    score_delta: float
    original_level: str
    scenario_level: str
    changed_factors: List[Dict[str, Any]]
    explanation: str

class EndTaskResponse(BaseModel):
    status: str = "success"
    message: str = "Sensitive session data has been deleted."
    result_preserved: bool = True
    ended_at: str
