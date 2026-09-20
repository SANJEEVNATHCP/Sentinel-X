"""
FraudLens AI - User Profile Schemas
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr

class UserProfileResponse(BaseModel):
    name: str
    email: EmailStr
    created_at: datetime
    total_investigations: int
    high_risk_count: int
    last_investigation: Optional[str] = None

class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
