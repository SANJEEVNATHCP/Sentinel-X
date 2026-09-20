"""
FraudLens AI - Privacy Policy & Explicit Session Purge API Endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.common import APIResponse
from app.services.cleanup_service import CleanupService

from app.models.investigation import Investigation
from app.models.investigation_result import InvestigationResult
from app.models.uploaded_file import UploadedFile
import os

router = APIRouter(prefix="/api/privacy", tags=["Privacy"])

@router.get("", response_model=APIResponse[dict])
def get_privacy_policy_overview():
    """Returns application data minimization commitments and raw-data purge guarantees."""
    return APIResponse(data={
        "data_retention_policy": "Zero long-term storage of raw files.",
        "raw_data_policy": "All uploaded documents, spreadsheets, and temporary scratchpads are permanently deleted upon task conclusion.",
        "derived_results_policy": "Derived risk scores, auditable evidence items, and executive summaries remain accessible in your personal Results history until explicitly deleted.",
        "gdpr_dpdp_compliance": "Designed to adhere to data minimization under India DPDP Act and GDPR Article 5(1)(c)."
    })

@router.post("/delete-session", response_model=APIResponse[dict])
def delete_all_active_session_data(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Executes immediate manual purge of any orphaned temporary files."""
    cleaned = CleanupService.cleanup_old_temp_files(max_age_hours=0)
    return APIResponse(message="Immediate session purge completed", data={"files_purged": cleaned})

@router.post("/wipe-all", response_model=APIResponse[dict])
def wipe_all_user_data(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Permanently purges all user investigations, derived results, uploaded files, and temporary scratchpads."""
    cleaned = CleanupService.cleanup_old_temp_files(max_age_hours=0)

    invs = db.query(Investigation).filter(Investigation.user_id == current_user.id).all()
    inv_ids = [inv.id for inv in invs]

    if inv_ids:
        files = db.query(UploadedFile).filter(UploadedFile.investigation_id.in_(inv_ids)).all()
        for f in files:
            if f.stored_path and os.path.exists(f.stored_path):
                try:
                    os.remove(f.stored_path)
                except Exception:
                    pass
            db.delete(f)

        db.query(InvestigationResult).filter(InvestigationResult.user_id == current_user.id).delete(synchronize_session=False)
        db.query(Investigation).filter(Investigation.user_id == current_user.id).delete(synchronize_session=False)
        db.commit()

    return APIResponse(
        message="All user data, investigation history, and session files have been permanently cleared",
        data={"files_purged": cleaned, "investigations_cleared": len(inv_ids)}
    )

