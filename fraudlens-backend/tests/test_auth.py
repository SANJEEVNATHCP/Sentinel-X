"""
FraudLens AI - Authentication Test Suite
"""

def test_user_registration(client):
    res = client.post("/api/auth/register", json={
        "name": "Jane Doe",
        "email": "jane_doe_test@example.com",
        "password": "SecurePassword@123",
        "confirm_password": "SecurePassword@123"
    })
    assert res.status_code == 200
    data = res.json()["data"]
    assert "access_token" in data
    assert data["user"]["email"] == "jane_doe_test@example.com"

def test_duplicate_registration_fails(client):
    payload = {
        "name": "Duplicate User",
        "email": "duplicate_test@example.com",
        "password": "SecurePassword@123",
        "confirm_password": "SecurePassword@123"
    }
    res1 = client.post("/api/auth/register", json=payload)
    assert res1.status_code == 200
    
    res2 = client.post("/api/auth/register", json=payload)
    assert res2.status_code == 400
    assert "already exists" in res2.json()["message"]

def test_login_success(client):
    res = client.post("/api/auth/login", json={
        "email": "test_analyst@fraudlens.ai",
        "password": "TestPassword@123"
    })
    assert res.status_code == 200
    assert "access_token" in res.json()["data"]

def test_login_invalid_password(client):
    res = client.post("/api/auth/login", json={
        "email": "test_analyst@fraudlens.ai",
        "password": "WrongPassword@999"
    })
    assert res.status_code == 401

def test_get_me(client, auth_headers):
    res = client.get("/api/auth/me", headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["data"]["email"] == "test_analyst@fraudlens.ai"
