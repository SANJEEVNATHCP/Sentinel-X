"""Generate synthetic data and train the supervised and anomaly models."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

from .anomaly import train_anomaly_model
from .features import engineer_features, save_feature_metadata
from .model_utils import ANOMALY_MODEL_PATH, DATA_DIR, FRAUD_MODEL_PATH, METADATA_PATH
from .validation import require_valid_transactions

SEED = 42


def generate_demo_transactions(count: int = 2400) -> pd.DataFrame:
    rng = np.random.default_rng(SEED)
    
    # 85% normal transactions, 15% fraudulent transactions
    n_fraud = int(count * 0.15)
    n_normal = count - n_fraud

    # --- Normal Transactions Baseline ---
    normal_avg = np.maximum(200, rng.normal(650, 150, n_normal))
    normal_ratio = rng.uniform(0.3, 2.2, n_normal)
    normal_amt = (normal_avg * normal_ratio).round(2)
    normal_hours = rng.integers(6, 24, n_normal)
    normal_new_dev = rng.binomial(1, 0.03, n_normal)
    normal_new_ben = rng.binomial(1, 0.04, n_normal)
    normal_vel = rng.integers(0, 4, n_normal)
    normal_loc = np.clip(rng.normal(0.08, 0.06, n_normal), 0, 0.3)
    normal_alerts = rng.binomial(1, 0.01, n_normal)

    timestamps_normal = pd.Timestamp("2025-01-01", tz="UTC") + pd.to_timedelta(rng.integers(0, 180 * 24 * 60, n_normal), unit="m")
    timestamps_normal = timestamps_normal.normalize() + pd.to_timedelta(normal_hours, unit="h") + pd.to_timedelta(rng.integers(0, 60, n_normal), unit="m")

    df_normal = pd.DataFrame({
        "transaction_id": [f"TXN{i + 1:04d}" for i in range(n_normal)],
        "user_id": [f"USER_{rng.integers(100, 180):03d}" for _ in range(n_normal)],
        "amount": normal_amt, "timestamp": timestamps_normal,
        "device_id": [f"DEV_{rng.integers(1, 80):02d}" for _ in range(n_normal)],
        "beneficiary_id": [f"BEN_{rng.integers(1, 250):03d}" for _ in range(n_normal)],
        "location_region": rng.choice(["NORTH", "SOUTH", "EAST", "WEST"], n_normal),
        "transaction_frequency": (normal_vel + rng.integers(1, 4, n_normal)).astype(float),
        "avg_amount": normal_avg.round(2), "is_new_device": normal_new_dev,
        "is_new_beneficiary": normal_new_ben, "location_deviation": normal_loc.round(3),
        "transactions_previous_hour": normal_vel.astype(float), "beneficiary_count": rng.integers(1, 6, n_normal).astype(float),
        "previous_fraud_alerts": normal_alerts.astype(float), "fraud_label": 0,
    })

    # --- Fraud Transactions ---
    fraud_avg = np.maximum(200, rng.normal(650, 150, n_fraud))
    pattern = rng.choice(["takeover", "velocity", "high_amt"], n_fraud, p=[0.45, 0.30, 0.25])
    fraud_ratio = np.where(pattern == "high_amt", rng.uniform(8.0, 30.0, n_fraud),
                  np.where(pattern == "takeover", rng.uniform(4.5, 12.0, n_fraud),
                           rng.uniform(1.8, 4.0, n_fraud)))
    fraud_amt = (fraud_avg * fraud_ratio).round(2)
    fraud_hours = np.where(rng.random(n_fraud) < 0.6, rng.integers(0, 6, n_fraud), rng.integers(6, 24, n_fraud))
    fraud_new_dev = np.where(pattern == "velocity", rng.binomial(1, 0.3, n_fraud), rng.binomial(1, 0.85, n_fraud))
    fraud_new_ben = np.where(pattern == "velocity", rng.binomial(1, 0.4, n_fraud), rng.binomial(1, 0.90, n_fraud))
    fraud_vel = np.where(pattern == "velocity", rng.integers(6, 15, n_fraud), rng.integers(1, 5, n_fraud))
    fraud_loc = np.clip(rng.normal(0.65, 0.18, n_fraud), 0.2, 1.0)
    fraud_alerts = np.where(pattern == "high_amt", rng.integers(1, 4, n_fraud), rng.binomial(1, 0.3, n_fraud))

    timestamps_fraud = pd.Timestamp("2025-01-01", tz="UTC") + pd.to_timedelta(rng.integers(0, 180 * 24 * 60, n_fraud), unit="m")
    timestamps_fraud = timestamps_fraud.normalize() + pd.to_timedelta(fraud_hours, unit="h") + pd.to_timedelta(rng.integers(0, 60, n_fraud), unit="m")

    df_fraud = pd.DataFrame({
        "transaction_id": [f"TXN{n_normal + i + 1:04d}" for i in range(n_fraud)],
        "user_id": [f"USER_{rng.integers(100, 180):03d}" for _ in range(n_fraud)],
        "amount": fraud_amt, "timestamp": timestamps_fraud,
        "device_id": [f"DEV_{rng.integers(81, 120):02d}" for _ in range(n_fraud)],
        "beneficiary_id": [f"BEN_{rng.integers(251, 400):03d}" for _ in range(n_fraud)],
        "location_region": rng.choice(["NORTH", "SOUTH", "EAST", "WEST"], n_fraud),
        "transaction_frequency": (fraud_vel + rng.integers(2, 6, n_fraud)).astype(float),
        "avg_amount": fraud_avg.round(2), "is_new_device": fraud_new_dev,
        "is_new_beneficiary": fraud_new_ben, "location_deviation": fraud_loc.round(3),
        "transactions_previous_hour": fraud_vel.astype(float), "beneficiary_count": rng.integers(4, 15, n_fraud).astype(float),
        "previous_fraud_alerts": fraud_alerts.astype(float), "fraud_label": 1,
    })

    data = pd.concat([df_normal, df_fraud], ignore_index=True)

    controlled = {
        "transaction_id": "TXN5721", "user_id": "USER_102", "amount": 24999.0,
        "timestamp": "2025-06-29T02:45:00Z", "device_id": "DEV_NEW", "beneficiary_id": "BEN_NEW",
        "location_region": "UNKNOWN", "transaction_frequency": 12.0, "avg_amount": 650.0,
        "is_new_device": 1, "is_new_beneficiary": 1, "location_deviation": 1.0,
        "transactions_previous_hour": 9.0, "beneficiary_count": 12.0, "previous_fraud_alerts": 2,
        "fraud_label": 1,
    }
    data = pd.concat([data, pd.DataFrame([controlled])], ignore_index=True)
    return data



def train_models(data: pd.DataFrame | None = None) -> dict[str, str]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    data = generate_demo_transactions() if data is None else data.copy()
    require_valid_transactions(data, require_label=True)
    data.to_csv(DATA_DIR / "demo_transactions.csv", index=False)
    features = engineer_features(data)
    labels = data["fraud_label"].astype(int)
    train_x, test_x, train_y, test_y = train_test_split(features, labels, test_size=0.25, random_state=SEED, stratify=labels)
    positives = max(1, int(train_y.sum()))
    negatives = max(1, int((train_y == 0).sum()))
    model = XGBClassifier(n_estimators=180, max_depth=4, learning_rate=0.06, subsample=0.85, colsample_bytree=0.85, scale_pos_weight=negatives / positives, objective="binary:logistic", eval_metric="logloss", random_state=SEED, n_jobs=2)
    model.fit(train_x, train_y)
    joblib.dump(model, FRAUD_MODEL_PATH)
    train_anomaly_model(features, ANOMALY_MODEL_PATH)
    save_feature_metadata(METADATA_PATH)
    split = {"test_indices": test_x.index.tolist()}
    (DATA_DIR / "split.json").write_text(json.dumps(split), encoding="utf-8")
    return {"fraud_model": str(FRAUD_MODEL_PATH), "anomaly_model": str(ANOMALY_MODEL_PATH), "rows": str(len(data))}


if __name__ == "__main__":
    print(json.dumps(train_models(), indent=2))
