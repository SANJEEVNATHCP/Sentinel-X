from ml.predict import get_model_working, predict_dataframe, predict_transaction


def transaction():
    return {"transaction_id": "TXN5721", "amount": 24999, "timestamp": "2025-06-29T02:45:00Z", "avg_amount": 650, "is_new_device": True, "is_new_beneficiary": True, "location_deviation": 1, "transactions_previous_hour": 9, "beneficiary_count": 12, "previous_fraud_alerts": 2, "transaction_frequency": 12}


def test_prediction_and_shap():
    result = predict_transaction(transaction())
    assert 0 <= result["risk_score"] <= 100
    assert result["risk_level"] in {"Low", "Medium", "High", "Critical"}
    assert result["top_risk_factors"]
    assert all("feature" in factor and "contribution" in factor for factor in result["top_risk_factors"])
    assert get_model_working(transaction())["model_name"] == "XGBoost"


def test_multiple_predictions():
    results = predict_dataframe(__import__("pandas").DataFrame([transaction(), {**transaction(), "transaction_id": "TXN5722", "amount": 100}]))
    assert len(results) == 2
