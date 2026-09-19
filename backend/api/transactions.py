from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.database.models import Alert, Transaction
from backend.schemas.transaction import (
    ExplanationResponse,
    RiskResponse,
    TransactionResponse,
)
from backend.services.ml_service import explain_transaction, predict_transaction

router = APIRouter(prefix="/api/transactions", tags=["Transactions"])


@router.get(
    "/{transaction_id}",
    response_model=TransactionResponse,
    summary="Retrieve transaction details",
    description="Fetches full transaction information by transaction_id for the UI and AI Investigator.",
)
def get_transaction(transaction_id: str, db: Session = Depends(get_db)):
    """Fetches a specific transaction by its transaction_id."""
    clean_id = transaction_id.strip()
    if not clean_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid transaction ID provided.",
        )

    transaction = db.query(Transaction).filter_by(transaction_id=clean_id).first()
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction '{clean_id}' not found.",
        )

    return transaction


@router.get(
    "/{transaction_id}/risk",
    response_model=RiskResponse,
    summary="Get ML fraud risk assessment",
    description="Returns risk score, risk level, and anomaly score produced by the ML model.",
)
def get_transaction_risk(transaction_id: str, db: Session = Depends(get_db)):
    """Exposes ML fraud detection risk assessment for a transaction."""
    clean_id = transaction_id.strip()
    if not clean_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid transaction ID provided.",
        )

    transaction = db.query(Transaction).filter_by(transaction_id=clean_id).first()
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction '{clean_id}' not found.",
        )

    # Check for pre-existing Alert in DB to maintain consistency if in fallback mode
    existing_alert = db.query(Alert).filter_by(transaction_id=clean_id).first()

    payload = {
        "transaction_id": transaction.transaction_id,
        "user_id": transaction.user_id,
        "amount": transaction.amount,
        "timestamp": transaction.timestamp.isoformat() if transaction.timestamp else None,
        "device_id": transaction.device_id,
        "beneficiary_id": transaction.beneficiary_id,
        "location": transaction.location,
        "is_new_device": transaction.is_new_device,
        "is_new_beneficiary": transaction.is_new_beneficiary,
        "existing_alert": existing_alert,
    }

    try:
        prediction = predict_transaction(payload)
        return RiskResponse(
            transaction_id=prediction["transaction_id"],
            risk_score=prediction["risk_score"],
            risk_level=prediction["risk_level"],
            anomaly_score=prediction["anomaly_score"],
            model_status=prediction.get("model_status"),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to retrieve risk prediction: {str(e)}",
        )


@router.get(
    "/{transaction_id}/explanation",
    response_model=ExplanationResponse,
    summary="Get SHAP feature impact explanation",
    description="Returns SHAP / risk factor attributions explaining why the transaction was flagged.",
)
def get_transaction_explanation(transaction_id: str, db: Session = Depends(get_db)):
    """Exposes SHAP feature contributions explaining transaction suspicion."""
    clean_id = transaction_id.strip()
    if not clean_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid transaction ID provided.",
        )

    transaction = db.query(Transaction).filter_by(transaction_id=clean_id).first()
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction '{clean_id}' not found.",
        )

    payload = {
        "transaction_id": transaction.transaction_id,
        "user_id": transaction.user_id,
        "amount": transaction.amount,
        "timestamp": transaction.timestamp.isoformat() if transaction.timestamp else None,
        "device_id": transaction.device_id,
        "beneficiary_id": transaction.beneficiary_id,
        "location": transaction.location,
        "is_new_device": transaction.is_new_device,
        "is_new_beneficiary": transaction.is_new_beneficiary,
    }

    try:
        explanation = explain_transaction(payload)
        return ExplanationResponse(
            transaction_id=explanation["transaction_id"],
            factors=explanation.get("factors", []),
            model_status=explanation.get("model_status"),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to retrieve SHAP explanation: {str(e)}",
        )
