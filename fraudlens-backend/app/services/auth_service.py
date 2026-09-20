"""
FraudLens AI - Authentication Service
Handles registration, login verification, and token issuance.
"""

from datetime import datetime
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.audit_log import AuditLog
from app.schemas.auth import UserRegisterRequest, UserLoginRequest, TokenResponse, UserResponse
from app.security import get_password_hash, verify_password, create_access_token
from app.exceptions import ValidationError, AuthenticationError
from app.utils.validation import validate_email_format, validate_password_strength

class AuthService:
    @staticmethod
    def register_user(db: Session, req: UserRegisterRequest, request_id: str = None) -> TokenResponse:
        cleaned_email = validate_email_format(req.email)
        
        if req.password != req.confirm_password:
            raise ValidationError("Password and confirmation do not match")
            
        validate_password_strength(req.password)

        existing = db.query(User).filter(User.email == cleaned_email).first()
        if existing:
            raise ValidationError("An account with this email address already exists")

        user = User(
            full_name=req.name.strip(),
            email=cleaned_email,
            password_hash=get_password_hash(req.password),
            created_at=datetime.utcnow()
        )
        db.add(user)
        db.flush()

        audit = AuditLog(
            user_id=user.id,
            action="USER_REGISTER",
            resource_type="USER",
            resource_id=user.id,
            request_id=request_id,
            status="SUCCESS"
        )
        db.add(audit)
        db.commit()
        db.refresh(user)

        token = create_access_token({"sub": user.id, "email": user.email})
        return TokenResponse(
            access_token=token,
            user=UserResponse.model_validate(user)
        )

    @staticmethod
    def login_user(db: Session, req: UserLoginRequest, request_id: str = None) -> TokenResponse:
        cleaned_email = validate_email_format(req.email)
        user = db.query(User).filter(User.email == cleaned_email).first()
        
        if not user or not verify_password(req.password, user.password_hash):
            raise AuthenticationError("Invalid email or password")
            
        if not user.is_active:
            raise AuthenticationError("Account is currently disabled")

        user.last_login_at = datetime.utcnow()
        audit = AuditLog(
            user_id=user.id,
            action="USER_LOGIN",
            resource_type="USER",
            resource_id=user.id,
            request_id=request_id,
            status="SUCCESS"
        )
        db.add(audit)
        db.commit()
        db.refresh(user)

        token = create_access_token({"sub": user.id, "email": user.email})
        return TokenResponse(
            access_token=token,
            user=UserResponse.model_validate(user)
        )
