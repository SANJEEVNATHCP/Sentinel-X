"""CSV/XLSX statement ingestion with conservative fallbacks."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

ALIASES = {
    "date": ["date", "timestamp", "datetime", "transaction date", "value date"],
    "description": ["description", "narration", "details", "remarks"],
    "debit": ["debit", "withdrawal", "withdrawals", "dr", "debit amount"],
    "credit": ["credit", "deposit", "deposits", "cr", "credit amount"],
    "amount": ["amount", "transaction amount", "value"],
    "balance": ["balance", "closing balance", "available balance"],
    "reference": ["reference", "ref", "transaction reference", "reference no"],
    "transaction_id": ["transaction_id", "transaction id", "id", "reference"],
}


def _normalized_columns(columns: list[Any]) -> dict[str, str]:
    normalized = {str(column).strip().lower().replace("_", " "): column for column in columns}
    result: dict[str, str] = {}
    for canonical, aliases in ALIASES.items():
        for alias in aliases:
            if alias in normalized:
                result[canonical] = normalized[alias]
                break
    return result


def load_statement(path: str | Path) -> pd.DataFrame:
    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(f"Statement file not found: {source}")
    try:
        raw = pd.read_csv(source) if source.suffix.lower() == ".csv" else pd.read_excel(source)
    except Exception as exc:
        raise ValueError(f"Could not read statement file: {source.name}") from exc
    columns = _normalized_columns(list(raw.columns))
    if "date" not in columns:
        raise ValueError("Statement needs a date/timestamp column")
    result = pd.DataFrame()
    result["timestamp"] = pd.to_datetime(raw[columns["date"]], errors="coerce", utc=True)
    if "amount" in columns:
        result["amount"] = pd.to_numeric(raw[columns["amount"]], errors="coerce").abs()
    else:
        debit = pd.to_numeric(raw[columns["debit"]], errors="coerce") if "debit" in columns else 0
        credit = pd.to_numeric(raw[columns["credit"]], errors="coerce") if "credit" in columns else 0
        result["amount"] = pd.Series(debit, index=raw.index).fillna(0).abs() + pd.Series(credit, index=raw.index).fillna(0).abs()
    result["description"] = raw[columns["description"]].fillna("").astype(str) if "description" in columns else ""
    result["reference"] = raw[columns["reference"]].fillna("").astype(str) if "reference" in columns else ""
    if "transaction_id" in columns:
        result["transaction_id"] = raw[columns["transaction_id"]].fillna("").astype(str)
    else:
        result["transaction_id"] = [f"STMT_{index:05d}" for index in range(len(result))]
    result = result.dropna(subset=["timestamp", "amount"])
    result = result[result["amount"] > 0].drop_duplicates(subset=["transaction_id"])
    result["user_id"] = "STATEMENT_USER"
    result["device_id"] = "UNKNOWN"
    result["beneficiary_id"] = "UNKNOWN"
    result["location_region"] = "UNKNOWN"
    result["transaction_frequency"] = 0.0
    result["avg_amount"] = result["amount"].expanding().mean().shift(1).fillna(result["amount"].mean())
    result["is_new_device"] = False
    result["is_new_beneficiary"] = False
    result["location_deviation"] = 0.0
    result["transactions_previous_hour"] = 0.0
    result["beneficiary_count"] = 0.0
    result["previous_fraud_alerts"] = 0.0
    return result.reset_index(drop=True)


def load_transactions(path: str | Path) -> pd.DataFrame:
    return load_statement(path)
