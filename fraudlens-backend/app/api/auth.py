"""
FraudLens AI - Authentication API Endpoints
"""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import UserRegisterRequest, UserLoginRequest, TokenResponse, UserResponse
from app.schemas.common import APIResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=APIResponse[TokenResponse])
def register(req: UserRegisterRequest, request: Request, db: Session = Depends(get_db)):
    """Registers a new user account and returns signed JWT access token."""
    request_id = getattr(request.state, "request_id", None)
    res = AuthService.register_user(db, req, request_id)
    return APIResponse(message="Account successfully created", data=res)

@router.post("/login", response_model=APIResponse[TokenResponse])
def login(req: UserLoginRequest, request: Request, db: Session = Depends(get_db)):
    """Authenticates credentials and issues signed JWT access token."""
    request_id = getattr(request.state, "request_id", None)
    res = AuthService.login_user(db, req, request_id)
    return APIResponse(message="Login successful", data=res)

@router.post("/logout", response_model=APIResponse[dict])
def logout(current_user: User = Depends(get_current_user)):
    """Stateless JWT logout confirmation endpoint."""
    return APIResponse(message="Successfully logged out", data={"logged_out": True})

@router.get("/me", response_model=APIResponse[UserResponse])
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Returns the authenticated user profile."""
    return APIResponse(data=UserResponse.model_validate(current_user))
