"""Validation for normalized transaction data."""

from __future__ import annotations

from typing import Any

import pandas as pd

REQUIRED_COLUMNS = ("transaction_id", "amount", "timestamp")


def validate_transactions(data: pd.DataFrame, require_label: bool = False) -> dict[str, Any]:
    errors: list[str] = []
    if not isinstance(data, pd.DataFrame) or data.empty:
        return {"valid": False, "errors": ["Transaction data is empty or not a DataFrame"]}
    missing = [column for column in REQUIRED_COLUMNS if column not in data.columns]
    if missing:
        errors.append(f"Missing required columns: {', '.join(missing)}")
    if require_label and "fraud_label" not in data.columns:
        errors.append("Missing required column: fraud_label")
    if "amount" in data:
        amounts = pd.to_numeric(data["amount"], errors="coerce")
        if amounts.isna().any() or not amounts.map(pd.api.types.is_number).all():
            errors.append("Amount column contains invalid values")
        elif (amounts <= 0).any():
            errors.append("Amount column contains non-positive values")
    if "timestamp" in data:
        timestamps = pd.to_datetime(data["timestamp"], errors="coerce", utc=True)
        if timestamps.isna().any():
            errors.append("Timestamp column contains invalid dates")
    if "transaction_id" in data and data["transaction_id"].duplicated().any():
        errors.append("Duplicate transaction IDs found")
    if "fraud_label" in data:
        labels = pd.to_numeric(data["fraud_label"], errors="coerce")
        if labels.isna().any() or not labels.isin([0, 1]).all():
            errors.append("fraud_label must contain only 0 or 1")
    return {"valid": not errors, "errors": errors}


def require_valid_transactions(data: pd.DataFrame, require_label: bool = False) -> None:
    result = validate_transactions(data, require_label=require_label)
    if not result["valid"]:
        raise ValueError("Invalid transaction data: " + "; ".join(result["errors"]))
