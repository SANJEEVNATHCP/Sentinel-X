import pandas as pd

from ml.features import FEATURE_COLUMNS, engineer_features


def test_feature_generation_and_ratio():
    frame = pd.DataFrame([{"transaction_id": "T1", "amount": 24999, "timestamp": "2025-01-01T02:45:00Z", "avg_amount": 650, "is_new_device": True, "is_new_beneficiary": True, "transactions_previous_hour": 9, "location_deviation": 1}])
    features = engineer_features(frame)
    assert list(features.columns) == FEATURE_COLUMNS
    assert round(features.iloc[0]["amount_deviation"], 2) == 38.46
    assert features.iloc[0]["unusual_hour_flag"] == 1
