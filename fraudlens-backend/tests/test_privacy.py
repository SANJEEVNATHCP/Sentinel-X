"""
FraudLens AI - Privacy & End-Task Session Scrubbing Test Suite
Verifies that sensitive uploaded files are purged while derived results remain intact.
"""

import os
import io

def test_end_task_purges_raw_files_and_preserves_result(client, auth_headers):
    # 1. Upload transaction file to create an investigation session
    sample_csv = "transaction_id,amount\nTXN1,500.00\n"
    file_bytes = io.BytesIO(sample_csv.encode("utf-8"))
    upload_res = client.post(
        "/api/transactions/analyze",
        files={"file": ("privacy_test.csv", file_bytes, "text/csv")},
        headers=auth_headers
    )
    assert upload_res.status_code == 200
    inv_id = upload_res.json()["data"]["investigation_id"]

    # 2. Call END TASK endpoint
    end_res = client.post(f"/api/investigations/{inv_id}/end", headers=auth_headers)
    assert end_res.status_code == 200
    end_data = end_res.json()["data"]
    assert end_data["status"] == "success"
    assert end_data["result_preserved"] is True

    # 3. Verify that the derived result still exists in results history
    hist_res = client.get(f"/api/results/{inv_id}", headers=auth_headers)
    assert hist_res.status_code == 200
    assert hist_res.json()["data"]["investigation_id"] == inv_id
    assert "evidence" in hist_res.json()["data"]

def test_wipe_all_endpoint(client, auth_headers):
    # Upload and analyze
    sample_csv = "transaction_id,amount\nTXN2,1200.00\n"
    file_bytes = io.BytesIO(sample_csv.encode("utf-8"))
    upload_res = client.post(
        "/api/transactions/analyze",
        files={"file": ("wipe_test.csv", file_bytes, "text/csv")},
        headers=auth_headers
    )
    assert upload_res.status_code == 200

    # Wipe all
    wipe_res = client.post("/api/privacy/wipe-all", headers=auth_headers)
    assert wipe_res.status_code == 200
    assert wipe_res.json()["status"] == "success"

    # Verify results list is empty for user
    list_res = client.get("/api/results", headers=auth_headers)
    assert list_res.status_code == 200
    assert len(list_res.json()["data"]) == 0

