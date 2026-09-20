"""Run the complete controlled FraudSentinel X demonstration."""

from __future__ import annotations

import json

from ml.model_utils import DATA_DIR
from ml.predict import get_model_working, predict_transaction
from ml.train import train_models


def main() -> None:
    if not (DATA_DIR / "demo_transactions.csv").exists():
        train_models()
    transaction = {
        "transaction_id": "TXN5721", "user_id": "USER_102", "amount": 24999,
        "timestamp": "2025-06-29T02:45:00Z", "device_id": "DEV_NEW", "beneficiary_id": "BEN_NEW",
        "location_region": "UNKNOWN", "transaction_frequency": 12, "avg_amount": 650,
        "is_new_device": True, "is_new_beneficiary": True, "location_deviation": 1,
        "transactions_previous_hour": 9, "beneficiary_count": 12, "previous_fraud_alerts": 2,
    }
    result = predict_transaction(transaction)
    print("\n" + "=" * 64 + "\nFRAUDSENTINEL X\nAI FRAUD DETECTION ENGINE\n" + "=" * 64)
    print("\nTRANSACTION\nTransaction ID : TXN5721\nAmount         : INR 24,999\nAverage Amount : INR 650\nTime           : 02:45 AM")
    print(f"\nFRAUD ANALYSIS\nRisk Score     : {result['risk_score']} / 100\nRisk Level     : {result['risk_level'].upper()}\nAnomaly Score  : {result['anomaly_score']}")
    print("\nTOP RISK FACTORS")
    for number, factor in enumerate(result["top_risk_factors"], 1):
        print(f"{number}. {factor['feature']} ({factor['direction']}, SHAP {factor['contribution']:+.3f})")
    print("\nMODEL\nModel          : XGBoost\nAnomaly Model  : Isolation Forest\nExplanation    : SHAP")
    print("\nFINAL JSON\n" + json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
