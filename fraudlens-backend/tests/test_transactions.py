"""
FraudLens AI - UPI Transaction Analysis & ML Test Suite
"""

import io

SAMPLE_CSV = """transaction_id,user_id,amount,timestamp,sender,receiver,upi_id,failed_attempts
TXN101,usr_test_123,1000.00,2026-09-10T10:00:00Z,Alice,Merchant A,m1@upi,0
TXN102,usr_test_123,1200.00,2026-09-11T12:00:00Z,Alice,Merchant B,m2@upi,0
TXN103,usr_test_123,900.00,2026-09-12T14:00:00Z,Alice,Merchant C,m3@upi,0
TXN104,usr_test_123,49000.00,2026-09-15T03:30:00Z,Alice,Unknown Payee,unverified@upi,3
"""

def test_analyze_transactions_flow(client, auth_headers):
    file_bytes = io.BytesIO(SAMPLE_CSV.encode("utf-8"))
    res = client.post(
        "/api/transactions/analyze",
        files={"file": ("test_statement.csv", file_bytes, "text/csv")},
        headers=auth_headers
    )
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["total_transactions"] == 4
    assert data["high_risk_count"] >= 1
    assert data["risk_score"] >= 50.0
    assert len(data["evidence"]) > 0
    assert any("Amount Anomaly" in e["signal"] for e in data["evidence"])
