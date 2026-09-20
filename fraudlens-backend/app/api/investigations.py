"""
FraudLens AI - Investigation Lifecycle & What-If API Endpoints
"""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.investigation import Investigation
from app.schemas.investigation import (
    InvestigationResponse, WhatIfRequest, WhatIfResponse, EndTaskResponse
)
from app.schemas.common import APIResponse
from app.services.risk_engine import RiskEngine
from app.services.privacy_service import PrivacyService
from app.exceptions import NotFoundError

router = APIRouter(prefix="/api/investigations", tags=["Investigations"])

@router.get("", response_model=APIResponse[list])
def list_investigations(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Returns all investigations initiated by the current user."""
    invs = db.query(Investigation).filter(Investigation.user_id == current_user.id).order_by(Investigation.created_at.desc()).all()
    return APIResponse(data=[InvestigationResponse.model_validate(i) for i in invs])

@router.get("/{investigation_id}", response_model=APIResponse[dict])
def get_investigation_progress(investigation_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Returns investigation progress, stages, and completion state for real-time frontend polling.
    """
    inv = db.query(Investigation).filter(
        Investigation.id == investigation_id,
        Investigation.user_id == current_user.id
    ).first()
    if not inv:
        raise NotFoundError("Investigation not found")

    res = inv.result
    return APIResponse(data={
        "id": inv.id,
        "type": inv.type,
        "status": inv.status,
        "progress": 100 if inv.status in ["COMPLETED", "ENDED"] else 65,
        "stage": "COMPLETED" if inv.status in ["COMPLETED", "ENDED"] else "GENERATING_EVIDENCE",
        "risk_score": inv.risk_score,
        "risk_level": inv.risk_level,
        "summary": inv.summary,
        "evidence": res.evidence_json if res else [],
        "risk_factors": res.risk_factors_json if res else [],
        "ai_summary": res.ai_summary if res else None,
        "created_at": inv.created_at.isoformat() + "Z",
        "ended_at": inv.ended_at.isoformat() + "Z" if inv.ended_at else None
    })

@router.post("/{investigation_id}/what-if", response_model=APIResponse[WhatIfResponse])
def run_what_if_scenario(
    investigation_id: str,
    req: WhatIfRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Recalculates risk score in real-time when the user toggles individual risk factors,
    enabling clear understanding of which evidence signals drive the classification.
    """
    inv = db.query(Investigation).filter(
        Investigation.id == investigation_id,
        Investigation.user_id == current_user.id
    ).first()
    if not inv:
        raise NotFoundError("Investigation not found")

    res = inv.result
    factors = res.risk_factors_json if res else []

    toggles = [{"signal_name": t.signal_name, "enabled": t.enabled} for t in req.toggled_signals]
    recalc = RiskEngine.recalculate_what_if(
        original_score=inv.risk_score,
        original_factors=factors,
        toggled_signals=toggles
    )

    response_data = WhatIfResponse(
        investigation_id=investigation_id,
        original_score=recalc["original_score"],
        scenario_score=recalc["scenario_score"],
        score_delta=recalc["score_delta"],
        original_level=inv.risk_level,
        scenario_level=recalc["scenario_level"],
        changed_factors=recalc["changed_factors"],
        explanation=recalc["explanation"]
    )
    return APIResponse(data=response_data)

@router.post("/{investigation_id}/end", response_model=APIResponse[EndTaskResponse])
def end_investigation(
    investigation_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    END TASK FLOW:
    Permanently deletes all raw uploaded files, PDFs, spreadsheets, and temporary scratch files.
    Preserves derived risk score, evidence signals, and executive summary in Results history.
    """
    request_id = getattr(request.state, "request_id", None)
    res = PrivacyService.end_investigation_and_purge_raw_data(
        db=db,
        user_id=current_user.id,
        investigation_id=investigation_id,
        request_id=request_id
    )
    return APIResponse(
        message="Sensitive session data has been deleted. Your investigation result remains available in Results.",
        data=EndTaskResponse(**res)
    )
