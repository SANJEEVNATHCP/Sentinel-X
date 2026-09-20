"""
FraudLens AI - Audit Log ORM Model
Auditable log of actions and privacy sanitization operations without storing PII.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from app.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=True, index=True)
    action = Column(String(100), nullable=False) # e.g. "USER_REGISTER", "END_TASK_CLEANUP", "DELETE_RESULT"
    resource_type = Column(String(100), nullable=False) # e.g. "INVESTIGATION", "USER"
    resource_id = Column(String(100), nullable=True)
    request_id = Column(String(100), nullable=True)
    status = Column(String(50), nullable=False) # "SUCCESS", "FAILURE"
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
