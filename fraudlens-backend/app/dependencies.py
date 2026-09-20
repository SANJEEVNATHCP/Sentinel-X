"""
FraudLens AI - FastAPI Dependencies
Injects database sessions, validates JWT Bearer tokens, and resolves current active user.
"""

from typing import Optional
from fastapi import Depends, Header, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.security import decode_access_token
from app.models.user import User
from app.exceptions import AuthenticationError

async def get_current_user(
    authorization: Optional[str] = Header(None),
    token: Optional[str] = Query(None),
    db: Session = Depends(get_db)
) -> User:
    """Extracts and verifies JWT token from Authorization header or query parameter, returning authenticated user."""
    jwt_token = None
    if authorization and authorization.startswith("Bearer "):
        jwt_token = authorization.split(" ", 1)[1].strip()
    elif token:
        jwt_token = token.strip()

    if not jwt_token:
        raise AuthenticationError("Missing or invalid Authorization credentials. Expected 'Bearer <token>' header or '?token=' query parameter.")

    payload = decode_access_token(jwt_token)
    user_id = payload.get("sub")
    
    if not user_id:
        raise AuthenticationError("Token payload missing user identifier")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise AuthenticationError("User associated with this token no longer exists")
    if not user.is_active:
        raise AuthenticationError("This user account is inactive")

    return user

async def get_optional_user(
    authorization: Optional[str] = Header(None),
    token: Optional[str] = Query(None),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Resolves authenticated user if valid token present; returns None otherwise."""
    jwt_token = None
    if authorization and authorization.startswith("Bearer "):
        jwt_token = authorization.split(" ", 1)[1].strip()
    elif token:
        jwt_token = token.strip()

    if not jwt_token:
        return None
    try:
        payload = decode_access_token(jwt_token)
        user_id = payload.get("sub")
        if user_id:
            return db.query(User).filter(User.id == user_id, User.is_active == True).first()
    except Exception:
        pass
    return None

