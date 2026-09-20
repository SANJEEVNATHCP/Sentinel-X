"""
FraudLens AI - LinkedIn Verification Test Suite
"""

def test_linkedin_valid_company_url(client, auth_headers):
    res = client.post("/api/company/linkedin", json={
        "linkedin_url": "https://www.linkedin.com/company/infosys"
    }, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["linkedin_found"] is True
    assert data["company_slug"] == "infosys"

def test_linkedin_rejects_personal_profile(client, auth_headers):
    res = client.post("/api/company/linkedin", json={
        "linkedin_url": "https://www.linkedin.com/in/john-doe-12345"
    }, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["linkedin_found"] is False
    assert data["verification_status"] == "INVALID_FORMAT"

def test_linkedin_rejects_job_listing(client, auth_headers):
    res = client.post("/api/company/linkedin", json={
        "linkedin_url": "https://www.linkedin.com/jobs/view/12345678"
    }, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["linkedin_found"] is False
    assert data["verification_status"] == "INVALID_FORMAT"
