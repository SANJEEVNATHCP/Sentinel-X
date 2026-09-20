"""
FraudLens AI - URL Security & SSRF Defense Test Suite
"""

def test_ssrf_blocks_localhost(client, auth_headers):
    """Ensures SSRF filter rejects loopback localhost target."""
    res = client.post("/api/scam/url", json={
        "url": "http://localhost:8080/admin"
    }, headers=auth_headers)
    assert res.status_code == 400
    assert "restricted" in res.json()["message"] or "blocked" in res.json()["message"]

def test_ssrf_blocks_ip_loopback(client, auth_headers):
    """Ensures SSRF filter rejects 127.0.0.1 IP."""
    res = client.post("/api/scam/url", json={
        "url": "http://127.0.0.1:5000"
    }, headers=auth_headers)
    assert res.status_code == 400

def test_ssrf_blocks_cloud_metadata(client, auth_headers):
    """Ensures SSRF filter blocks cloud instance metadata IP."""
    res = client.post("/api/scam/url", json={
        "url": "http://169.254.169.254/latest/meta-data/"
    }, headers=auth_headers)
    assert res.status_code == 400

def test_ssrf_blocks_file_scheme(client, auth_headers):
    """Ensures non-web protocols like file:// are blocked."""
    res = client.post("/api/scam/url", json={
        "url": "file:///etc/passwd"
    }, headers=auth_headers)
    assert res.status_code == 400
