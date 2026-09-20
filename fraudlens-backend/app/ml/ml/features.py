"""Shared feature engineering used by training and prediction."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

FEATURE_COLUMNS = [
    "amount", "transaction_hour", "day_of_week", "transaction_frequency",
    "avg_amount", "amount_deviation", "transactions_previous_hour",
    "beneficiary_count", "previous_fraud_alerts", "is_new_device",
    "is_new_beneficiary", "location_deviation", "unusual_hour_flag",
    "high_velocity_flag", "high_amount_flag",
]


def engineer_features(data: pd.DataFrame) -> pd.DataFrame:
    frame = data.copy()
    timestamps = pd.to_datetime(frame["timestamp"], errors="coerce", utc=True)
    frame["amount"] = pd.to_numeric(frame["amount"], errors="coerce").fillna(0).clip(lower=0)
    frame["transaction_hour"] = timestamps.dt.hour.fillna(12).astype(float)
    frame["day_of_week"] = timestamps.dt.dayofweek.fillna(0).astype(float)
    for column in ["transaction_frequency", "avg_amount", "transactions_previous_hour", "beneficiary_count", "previous_fraud_alerts", "location_deviation"]:
        values = frame[column] if column in frame else pd.Series(0, index=frame.index)
        frame[column] = pd.to_numeric(values, errors="coerce").fillna(0)
    for column in ["is_new_device", "is_new_beneficiary"]:
        frame[column] = frame.get(column, False).map(lambda value: int(bool(value))) if hasattr(frame.get(column, False), "map") else 0
    frame["avg_amount"] = frame["avg_amount"].clip(lower=0)
    frame["amount_deviation"] = frame["amount"] / frame["avg_amount"].replace(0, np.nan).fillna(1)
    frame["unusual_hour_flag"] = frame["transaction_hour"].isin([0, 1, 2, 3, 4, 5]).astype(float)
    frame["high_velocity_flag"] = (frame["transactions_previous_hour"] >= 5).astype(float)
    frame["high_amount_flag"] = (frame["amount_deviation"] >= 4).astype(float)
    return frame[FEATURE_COLUMNS].replace([np.inf, -np.inf], 0).fillna(0).astype(float)


def save_feature_metadata(path: Path) -> None:
    path.write_text(json.dumps({"feature_columns": FEATURE_COLUMNS}, indent=2), encoding="utf-8")
