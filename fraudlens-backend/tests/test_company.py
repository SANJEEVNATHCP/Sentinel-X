"""
FraudLens AI - Company Dataset Evaluation Test Suite
Verifies Active (real) vs Inactive (fake/defunct) classification based on the dataset.
"""

def test_company_active_verification(client, auth_headers):
    """Tests that active companies in dataset (e.g. Infosys, TCS, Wipro) are verified as Active/Real."""
    res = client.post("/api/company/verify", json={
        "company_name": "INFOSYS LIMITED",
        "domain": "infosys.com",
        "recruiter_email": "careers@infosys.com"
    }, headers=auth_headers)

    assert res.status_code == 200
    data = res.json()["data"]
    assert data["mca_verified"] is True
    assert data["company_status"].lower() == "active"
    assert data["cin"] == "L72200KA1981PLC013115"
    assert data["domain_match"] is True
    assert data["risk_level"] == "LOW"

def test_company_inactive_threat_flag(client, auth_headers):
    """Tests that inactive companies in dataset (e.g. South Bank Mosaics) are flagged as HIGH_RISK."""
    res = client.post("/api/company/verify", json={
        "company_name": "SOUTH BANK MOSAICS",
        "domain": "southbankmosaics.com"
    }, headers=auth_headers)

    assert res.status_code == 200
    data = res.json()["data"]
    assert data["mca_verified"] is True
    assert data["company_status"].lower() == "inactive"
    assert data["risk_level"] == "HIGH_RISK"
    assert "INACTIVE" in data["verification_note"]

def test_company_not_found(client, auth_headers):
    """Tests that unknown entities not in dataset are marked as UNVERIFIED without fake data."""
    res = client.post("/api/company/verify", json={
        "company_name": "NonExistentPhantomCorpXYZ123"
    }, headers=auth_headers)

    assert res.status_code == 200
    data = res.json()["data"]
    assert data["mca_verified"] is False
    assert data["company_status"] == "NOT_FOUND"
    assert data["risk_level"] == "UNVERIFIED"

def test_recruiter_domain_mismatch(client, auth_headers):
    """Tests detection when a recruiter communicates from a mismatched or free email."""
    res = client.post("/api/company/verify", json={
        "company_name": "TATA CONSULTANCY SERVICES LIMITED",
        "domain": "tcs.com",
        "recruiter_email": "tcs-recruitment-team@gmail.com"
    }, headers=auth_headers)

    assert res.status_code == 200
    data = res.json()["data"]
    assert data["domain_match"] is False
