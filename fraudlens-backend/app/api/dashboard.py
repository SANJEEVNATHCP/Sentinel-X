"""
FraudLens AI - Dashboard API Endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.common import APIResponse
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("", response_model=APIResponse[dict])
def get_dashboard(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Fetches verified activity metrics and recent investigations for the current user."""
    stats = DashboardService.get_user_dashboard(db, current_user.id)
    return APIResponse(data=stats)
