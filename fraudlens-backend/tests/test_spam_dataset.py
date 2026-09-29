"""
FraudLens AI - Spam Threat Feed Dataset Test Suite
"""

def test_spam_url_active_status(client, auth_headers):
    """Tests URL cataloged as ACTIVE in local dataset."""
    res = client.post("/api/scam/url", json={
        "url": "https://google-careers-example.xyz/internship"
    }, headers=auth_headers)

    assert res.status_code == 200
    data = res.json()["data"]
    assert data["local_dataset"]["dataset_found"] is True
    assert data["local_dataset"]["status"] == "ACTIVE"
    assert data["risk_score"] > 0

def test_spam_url_inactive_status(client, auth_headers):
    """Tests URL cataloged as INACTIVE in local dataset."""
    res = client.post("/api/scam/url", json={
        "url": "https://southbankmosaics.com"
    }, headers=auth_headers)

    assert res.status_code == 200
    data = res.json()["data"]
    assert data["local_dataset"]["dataset_found"] is True
    assert data["local_dataset"]["status"] == "INACTIVE"
    assert data["risk_score"] >= 35.0

def test_url_not_in_dataset(client, auth_headers):
    """Tests URL not present in dataset."""
    res = client.post("/api/scam/url", json={
        "url": "https://wikipedia.org"
    }, headers=auth_headers)

    assert res.status_code == 200
    data = res.json()["data"]
    assert data["local_dataset"]["dataset_found"] is False
    assert data["local_dataset"]["status"] == "NOT_FOUND"
