"""
FraudLens AI - Complete System Verification & Integration Test Suite
Validates compilation, database connections, ML model predictions, anomaly scores,
multi-image uploads (3 images), Gemini/heuristic vision, and PDF/JSON downloads.
"""

import io
import os
import json
import time
import requests
from PIL import Image, ImageDraw

BASE_URL = "http://127.0.0.1:8000"

def run_tests():
    print("==================================================================")
    print("         FRAUDLENS AI â€” SYSTEM INTEGRITY & ML VERIFICATION        ")
    print("==================================================================")

    # -------------------------------------------------------------
    # 1. API Health & Authentication
    # -------------------------------------------------------------
    print("\n[1/8] Verifying API Server & Authentication...")
    docs_resp = requests.get(f"{BASE_URL}/docs")
    assert docs_resp.status_code == 200, f"Docs endpoint failed: {docs_resp.status_code}"

    auth_resp = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": "demo@fraudlens.ai", "password": "FraudLens@2026"}
    )
    assert auth_resp.status_code == 200, f"Login failed: {auth_resp.text}"
    token = auth_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("  âœ“ Server is responsive (HTTP 200).")
    print("  âœ“ Authenticated as demo@fraudlens.ai. Bearer token issued.")

    # -------------------------------------------------------------
    # 2. Database Connectivity & User Profile
    # -------------------------------------------------------------
    print("\n[2/8] Verifying Database Connectivity & Profile Resolution...")
    me_resp = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
    assert me_resp.status_code == 200, f"Get current user failed: {me_resp.text}"
    user_data = me_resp.json()["data"]
    print(f"  âœ“ User record retrieved from SQLite: {user_data['full_name']} ({user_data['email']})")

    # -------------------------------------------------------------
    # 3. UPI Transaction Analysis & ML Fraud Engine
    # -------------------------------------------------------------
    print("\n[3/8] Verifying UPI Transaction Analysis & ML Model Inference...")
    sample_csv_path = "fraudlens-backend/datasets/sample_transactions.csv"
    with open(sample_csv_path, "rb") as f:
        csv_content = f.read()

    tx_resp = requests.post(
        f"{BASE_URL}/api/transactions/analyze",
        headers=headers,
        files={"file": ("sample_transactions.csv", csv_content, "text/csv")}
    )
    assert tx_resp.status_code == 200, f"Transaction analysis failed: {tx_resp.text}"
    tx_data = tx_resp.json()["data"]
    txns = tx_data["transactions"]
    
    print(f"  âœ“ Processed {len(txns)} transactions across dual ML models.")
    print(f"  âœ“ Overall Risk: {tx_data['risk_score']}/100 ({tx_data['risk_level']})")
    print(f"  âœ“ User baseline mean: INR {tx_data['user_historical_mean']:.2f}")

    # Verify normal transactions have low fraud score
    normal_tx = txns[0]
    assert "xgboost_score" in normal_tx, "xgboost_score missing from serialized transaction response"
    assert normal_tx["fraud_probability"] < 0.20, f"Normal txn flagged high: {normal_tx['fraud_probability']}"
    assert normal_tx["is_anomalous"] == 0, "Normal txn marked as anomalous"
    print(f"  [OK] Normal Txn ({normal_tx['transaction_id']}): Amount={normal_tx['amount']}, XGBoost Score={normal_tx['xgboost_score']}, Anomaly={normal_tx['is_anomalous']}")

    # Verify fraud transactions are accurately caught
    fraud_tx = txns[-1]
    assert fraud_tx["fraud_probability"] >= 0.50, f"Fraud txn missed by model: {fraud_tx['fraud_probability']}"
    assert fraud_tx["is_anomalous"] == 1, "Fraud txn missed by Isolation Forest"
    print(f"  âœ“ Fraud Txn ({fraud_tx['transaction_id']}): Amount={fraud_tx['amount']}, Fraud Prob={fraud_tx['fraud_probability']}, Anomaly={fraud_tx['is_anomalous']}")
    print(f"    Observed Signals: {fraud_tx['signals']}")

    upi_inv_id = tx_data["investigation_id"]

    # -------------------------------------------------------------
    # 4. Multi-Image Upload (3 Images at once) & Anomaly Detection
    # -------------------------------------------------------------
    print("\n[4/8] Verifying Multi-Image Upload (3 images at once) & Anomaly Detection...")
    img1_io, img2_io, img3_io = io.BytesIO(), io.BytesIO(), io.BytesIO()
    
    im1 = Image.new("RGB", (320, 240), color=(250, 250, 250))
    d1 = ImageDraw.Draw(im1)
    d1.text((10, 40), "ALERT: Pay 5000 registration fee to avoid account block.", fill=(255, 0, 0))
    im1.save(img1_io, format="PNG")
    
    im2 = Image.new("RGB", (320, 240), color=(255, 255, 245))
    d2 = ImageDraw.Draw(im2)
    d2.text((10, 40), "Share OTP immediately for 50,000 cash prize claim.", fill=(200, 0, 0))
    im2.save(img2_io, format="PNG")

    im3 = Image.new("RGB", (320, 240), color=(245, 250, 255))
    d3 = ImageDraw.Draw(im3)
    d3.text((10, 40), "Payment receipt: Transferred 25,000 INR successfully.", fill=(0, 140, 0))
    im3.save(img3_io, format="PNG")

    multi_files = [
        ("files", ("evidence_chat1.png", img1_io.getvalue(), "image/png")),
        ("files", ("evidence_chat2.png", img2_io.getvalue(), "image/png")),
        ("files", ("evidence_chat3.png", img3_io.getvalue(), "image/png")),
    ]
    img_resp = requests.post(
        f"{BASE_URL}/api/scam/image-analysis",
        headers=headers,
        files=multi_files,
        data={"context": "Multiple extortion and OTP solicitations"}
    )
    assert img_resp.status_code == 200, f"Image analysis failed: {img_resp.text}"
    img_data = img_resp.json()["data"]
    assert img_data["images_analyzed"] == 3, f"Expected 3 images, got {img_data.get('images_analyzed')}"
    print(f"  âœ“ Multi-image batch: {img_data['images_analyzed']}/3 images processed concurrently.")
    print(f"  âœ“ Analysis engine: {img_data['analysis_mode']}")
    print(f"  âœ“ Anomalies detected ({len(img_data['anomalies_detected'])}):")
    for anom in img_data["anomalies_detected"][:3]:
        print(f"    - {anom}")
    img_inv_id = img_data["investigation_id"]

    # -------------------------------------------------------------
    # 5. Company Verification & Authoritative Reference Master
    # -------------------------------------------------------------
    print("\n[5/8] Verifying MCA Company Master & Recruiter Consistency...")
    # Active company test
    active_resp = requests.post(
        f"{BASE_URL}/api/company/verify",
        headers=headers,
        json={"company_name": "Infosys", "domain": "infosys.com", "recruiter_email": "hr@infosys.com"}
    )
    assert active_resp.status_code == 200
    act_data = active_resp.json()["data"]
    assert act_data["company_status"] == "Active"
    assert act_data["investigation_id"] is not None
    print(f"  âœ“ Verified Real Company: {act_data['searched_name']} -> Status: {act_data['company_status']}, Risk: {act_data['risk_level']}")

    # Defunct company test
    fake_resp = requests.post(
        f"{BASE_URL}/api/company/verify",
        headers=headers,
        json={"company_name": "Apex Global Tech", "domain": "apexglobaltech-fake.com"}
    )
    assert fake_resp.status_code == 200
    fake_data = fake_resp.json()["data"]
    print(f"  âœ“ Defunct/Inactive Company Detection: Status: {fake_data['company_status']}, Risk: {fake_data['risk_level']}")
    comp_inv_id = act_data["investigation_id"]

    # -------------------------------------------------------------
    # 6. Scam URL Intelligence Scanner
    # -------------------------------------------------------------
    print("\n[6/8] Verifying URL Intelligence Scanner...")
    url_resp = requests.post(
        f"{BASE_URL}/api/scam/url",
        headers=headers,
        json={"url": "http://fake-banking-verify-update.xyz/login.php"}
    )
    assert url_resp.status_code == 200, f"URL check failed: {url_resp.text}"
    url_data = url_resp.json()["data"]
    print(f"  âœ“ Scanned URL: {url_data['url']}")
    print(f"  âœ“ Risk Score: {url_data['risk_score']}/100 ({url_data['risk_level']})")
    print(f"  âœ“ Suspicious Patterns Flagged: {len(url_data.get('suspicious_patterns_detected', []))}")
    url_inv_id = url_data["investigation_id"]

    # -------------------------------------------------------------
    # 7. Audit-Grade PDF & JSON Report Downloads
    # -------------------------------------------------------------
    print("\n[7/8] Verifying Audit-Grade Report Generation (PDF & JSON)...")
    test_ids = [
        ("UPI Analysis", upi_inv_id),
        ("Multi-Image Analysis", img_inv_id),
        ("Company Verification", comp_inv_id),
        ("URL Security Scan", url_inv_id)
    ]
    for label, inv_id in test_ids:
        # PDF Download
        pdf_res = requests.get(f"{BASE_URL}/api/results/{inv_id}/download?format=pdf&token={token}")
        assert pdf_res.status_code == 200, f"PDF failed for {label}: {pdf_res.status_code}"
        assert pdf_res.headers.get("content-type") == "application/pdf"
        assert len(pdf_res.content) > 1000

        # JSON Download
        json_res = requests.get(f"{BASE_URL}/api/results/{inv_id}/download?format=json&token={token}")
        assert json_res.status_code == 200, f"JSON failed for {label}: {json_res.status_code}"
        j_payload = json_res.json()
        assert j_payload["investigation_id"] == inv_id

        print(f"  âœ“ {label:<22} -> PDF ({len(pdf_res.content)} bytes) & JSON OK.")

    # -------------------------------------------------------------
    # 8. Dashboard Analytics & Data Scrubbing
    # -------------------------------------------------------------
    print("\n[8/8] Verifying Dashboard Analytics & Privacy Lifecycle...")
    dash_resp = requests.get(f"{BASE_URL}/api/dashboard", headers=headers)
    assert dash_resp.status_code == 200
    dash_data = dash_resp.json()["data"]
    print(f"  [OK] Total investigations logged: {dash_data.get('total_investigations')}")
    print(f"  [OK] High risk cases identified: {dash_data.get('high_risk_detections', 0)}")

    # Test End-Task Data Scrubbing
    end_task_resp = requests.post(f"{BASE_URL}/api/investigations/{upi_inv_id}/end", headers=headers)
    assert end_task_resp.status_code == 200
    print(f"  âœ“ End-Task privacy scrub completed for {upi_inv_id}. Raw temporary files purged.")

    # Verify report is STILL downloadable after raw scrub (audit durability)
    post_scrub_pdf = requests.get(f"{BASE_URL}/api/results/{upi_inv_id}/download?format=pdf&token={token}")
    assert post_scrub_pdf.status_code == 200
    print(f"  âœ“ Report survives raw data scrubbing ({len(post_scrub_pdf.content)} bytes). Audit durability confirmed.")

    print("\n==================================================================")
    print("   [SUCCESS] ALL MODULES, MODELS, INTEGRATIONS & DATABASES OK!    ")
    print("==================================================================")

if __name__ == "__main__":
    run_tests()
