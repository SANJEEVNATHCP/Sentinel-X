"""
FraudLens AI - Transaction Feature Engineering Module
Parses and derives behavioral metrics and deviation baselines from statement data.
"""

import pandas as pd
import numpy as np

def extract_transaction_features(df: pd.DataFrame) -> pd.DataFrame:
    """Extracts behavioral, temporal, and deviation features from transaction dataframes."""
    df = df.copy()

    # Amount normalization
    if "amount" in df.columns:
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0)
    else:
        for col in ["debit", "txn_amount", "transaction_amount", "Amount", "Debit", "DEBIT"]:
            if col in df.columns:
                df["amount"] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
                break
        else:
            df["amount"] = 0.0

    # Parse timestamps
    if "timestamp" in df.columns:
        df["dt"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df["hour"] = df["dt"].dt.hour.fillna(12)
        df["day_of_week"] = df["dt"].dt.dayofweek.fillna(0)
    elif "date" in df.columns or "Date" in df.columns:
        col = "date" if "date" in df.columns else "Date"
        df["dt"] = pd.to_datetime(df[col], errors="coerce")
        df["hour"] = df["dt"].dt.hour.fillna(12)
        df["day_of_week"] = df["dt"].dt.dayofweek.fillna(0)
    else:
        df["hour"] = 12
        df["day_of_week"] = 0

    # Historical baseline stats per user if user_id present
    user_col = "user_id" if "user_id" in df.columns else None
    if user_col:
        user_means = df.groupby(user_col)["amount"].transform("mean")
        user_stds = df.groupby(user_col)["amount"].transform("std").fillna(1.0)
        df["user_mean"] = user_means
        df["amount_ratio"] = df["amount"] / (df["user_mean"] + 1e-5)
    else:
        mean_amt = df["amount"].mean() if len(df) > 0 else 1.0
        df["user_mean"] = mean_amt
        df["amount_ratio"] = df["amount"] / (mean_amt + 1e-5)

    # Failed attempts
    if "failed_attempts" in df.columns:
        df["failed_attempts"] = pd.to_numeric(df["failed_attempts"], errors="coerce").fillna(0)
    else:
        df["failed_attempts"] = 0

    # Flag off-hours (e.g. 1 AM to 5 AM)
    df["is_night_txn"] = ((df["hour"] >= 1) & (df["hour"] <= 5)).astype(int)

    # Normalize transaction_id — support common UPI CSV column names
    if "transaction_id" not in df.columns:
        for col in ["txn_id", "Transaction_ID", "TransactionID", "txnid", "id", "ID", "Txn_ID", "ref_no", "reference_id"]:
            if col in df.columns:
                df["transaction_id"] = df[col].astype(str)
                break
        # else leave missing — transaction_service will fallback to TXN_{idx+1}

    # Normalize receiver_id — support common UPI CSV column names
    if "receiver_id" not in df.columns:
        for col in ["receiver", "Receiver", "upi_id", "UPI_ID", "beneficiary_id",
                    "Beneficiary_ID", "payee_id", "payee", "Payee",
                    "to_upi", "To_UPI", "receiver_upi", "vpa", "VPA"]:
            if col in df.columns:
                df["receiver_id"] = df[col].astype(str).str.strip()
                break

    return df
