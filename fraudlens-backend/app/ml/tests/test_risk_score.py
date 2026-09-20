from ml.risk_score import calculate_risk_score, risk_level


def test_risk_boundaries():
    assert risk_level(0) == "Low"
    assert risk_level(29) == "Low"
    assert risk_level(30) == "Medium"
    assert risk_level(60) == "High"
    assert risk_level(80) == "Critical"
    result = calculate_risk_score(1, 1, {"is_new_device": 1, "is_new_beneficiary": 1, "unusual_hour_flag": 1, "high_velocity_flag": 1, "high_amount_flag": 1})
    assert 0 <= result["risk_score"] <= 100
