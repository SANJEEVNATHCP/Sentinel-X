"""
FraudLens AI - Results History & Report Download Test Suite
"""

import io

def test_results_history_and_pdf_download(client, auth_headers):
    # Create an analysis result first
    sample_csv = "transaction_id,amount\nTXN_A,250.00\n"
    res_upload = client.post(
        "/api/transactions/analyze",
        files={"file": ("report_test.csv", io.BytesIO(sample_csv.encode("utf-8")), "text/csv")},
        headers=auth_headers
    )
    inv_id = res_upload.json()["data"]["investigation_id"]

    # 1. Query results list
    list_res = client.get("/api/results", headers=auth_headers)
    assert list_res.status_code == 200
    assert len(list_res.json()["data"]) >= 1

    # 2. Download JSON report
    json_res = client.get(f"/api/results/{inv_id}/download?format=json", headers=auth_headers)
    assert json_res.status_code == 200
    assert json_res.json()["investigation_id"] == inv_id

    # 3. Download PDF report
    pdf_res = client.get(f"/api/results/{inv_id}/download?format=pdf", headers=auth_headers)
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"
    assert len(pdf_res.content) > 100
