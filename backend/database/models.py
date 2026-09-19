from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from backend.database.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    user_id = Column(String(50), primary_key=True, index=True)
    avg_transaction_amount = Column(Float, nullable=False, default=0.0)
    normal_transaction_frequency = Column(Float, nullable=False, default=1.0)
    normal_location = Column(String(100), nullable=False)

    # Relationships
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")


class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id = Column(String(50), primary_key=True, index=True)
    user_id = Column(String(50), ForeignKey("users.user_id"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=utc_now, nullable=False)
    device_id = Column(String(100), nullable=False)
    beneficiary_id = Column(String(100), nullable=False)
    location = Column(String(100), nullable=False)
    is_new_device = Column(Boolean, default=False, nullable=False)
    is_new_beneficiary = Column(Boolean, default=False, nullable=False)

    # Relationships
    user = relationship("User", back_populates="transactions")
    alerts = relationship("Alert", back_populates="transaction", cascade="all, delete-orphan")
    investigations = relationship("Investigation", back_populates="transaction", cascade="all, delete-orphan")


class Alert(Base):
    __tablename__ = "alerts"

    alert_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    transaction_id = Column(String(50), ForeignKey("transactions.transaction_id"), nullable=False, index=True)
    risk_score = Column(Float, nullable=False)
    risk_level = Column(String(20), nullable=False)  # e.g., "HIGH", "MEDIUM", "LOW"
    status = Column(String(20), default="PENDING", nullable=False)  # e.g., "PENDING", "ESCALATED", "RESOLVED"
    created_at = Column(DateTime, default=utc_now, nullable=False)

    # Relationships
    transaction = relationship("Transaction", back_populates="alerts")


class Investigation(Base):
    __tablename__ = "investigations"

    investigation_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    transaction_id = Column(String(50), ForeignKey("transactions.transaction_id"), nullable=False, index=True)
    question = Column(Text, nullable=False)
    response = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    # Relationships
    transaction = relationship("Transaction", back_populates="investigations")
