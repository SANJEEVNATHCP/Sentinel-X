"""
FraudLens AI - UPI Transaction API Endpoints
"""

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.investigation import Investigation
from app.models.uploaded_file import UploadedFile as UploadedFileModel
from app.schemas.transaction import UPIAnalysisResponse
from app.schemas.common import APIResponse
from app.services.transaction_service import TransactionService
from app.utils.file_utils import save_upload_file_temporarily
from app.exceptions import NotFoundError

router = APIRouter(prefix="/api/transactions", tags=["Transactions"])

@router.post("/analyze", response_model=APIResponse[UPIAnalysisResponse])
async def analyze_transactions(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Accepts CSV/XLSX UPI transaction exports. Runs behavioral profile modeling,
    XGBoost fraud prediction (xgboost_fraud_model.joblib), and IsolationForest anomaly detection.
    Results are persisted to the database and downloadable as PDF or JSON.
    """
    # 1. Create Investigation entry
    inv = Investigation(
        user_id=current_user.id,
        type="UPI",
        status="PROCESSING",
        target_entity=file.filename or "Uploaded Statement"
    )
    db.add(inv)
    db.flush()

    # 2. Read file content once, then use it for both size tracking and parsing
    file_content = await file.read()
    file_size = len(file_content)

    # Reset stream pointer so save_upload_file_temporarily and TransactionService can read it
    await file.seek(0)
    temp_path = save_upload_file_temporarily(file)

    up_file = UploadedFileModel(
        investigation_id=inv.id,
        original_filename=file.filename or "statement.csv",
        stored_path=temp_path,
        file_type="SPREADSHEET",
        file_size_bytes=file_size
    )
    db.add(up_file)
    db.commit()

    # Reset stream pointer again for TransactionService parsing
    await file.seek(0)

    # 3. Process Transactions
    res = await TransactionService.process_transaction_file(
        db=db,
        user_id=current_user.id,
        file=file,
        investigation_id=inv.id
    )

    return APIResponse(message="Transaction analysis completed", data=res)

@router.get("/{investigation_id}", response_model=APIResponse[dict])
def get_transaction_batch(investigation_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    inv = db.query(Investigation).filter(
        Investigation.id == investigation_id,
        Investigation.user_id == current_user.id
    ).first()
    if not inv:
        raise NotFoundError("Investigation not found")

    res = inv.result
    return APIResponse(data={
        "investigation_id": inv.id,
        "risk_score": inv.risk_score,
        "risk_level": inv.risk_level,
        "summary": inv.summary,
        "evidence": inv.result.evidence_json if res else [],
        "created_at": inv.created_at.isoformat() + "Z"
    })
