"""
FraudLens AI - Standard Response Envelopes
Provides consistent JSON response structures across all endpoints.
"""

from typing import Generic, TypeVar, Optional, Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime

T = TypeVar("T")

class ResponseMetadata(BaseModel):
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    request_id: Optional[str] = None

class APIResponse(BaseModel, Generic[T]):
    status: str = "success"
    message: str = "Operation completed successfully"
    data: Optional[T] = None
    metadata: ResponseMetadata = Field(default_factory=ResponseMetadata)

class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
    error_code: str
    metadata: ResponseMetadata = Field(default_factory=ResponseMetadata)
