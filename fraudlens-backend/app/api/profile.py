"""
FraudLens AI - Profile API Endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.investigation import Investigation
from app.schemas.user import UserProfileResponse, UserUpdateRequest
from app.schemas.common import APIResponse

router = APIRouter(prefix="/api/profile", tags=["Profile"])

@router.get("", response_model=APIResponse[UserProfileResponse])
def get_profile(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    invs = db.query(Investigation).filter(Investigation.user_id == current_user.id).all()
    total = len(invs)
    high_risk = sum(1 for i in invs if i.risk_level in ["HIGH_RISK", "LIKELY_SCAM"])
    last_inv = invs[-1].created_at.strftime("%Y-%m-%d %H:%M") if invs else None

    profile_data = UserProfileResponse(
        name=current_user.full_name,
        email=current_user.email,
        created_at=current_user.created_at,
        total_investigations=total,
        high_risk_count=high_risk,
        last_investigation=last_inv
    )
    return APIResponse(data=profile_data)

@router.put("", response_model=APIResponse[dict])
def update_profile(req: UserUpdateRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if req.full_name:
        current_user.full_name = req.full_name.strip()
    if req.email:
        current_user.email = req.email.strip().lower()
    db.commit()
    return APIResponse(message="Profile updated successfully", data={"name": current_user.full_name, "email": current_user.email})
