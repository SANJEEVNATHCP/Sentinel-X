import io
import json
import requests
from PIL import Image, ImageDraw

BASE_URL = "http://127.0.0.1:8000"

def test_full_pipeline():
    print("=== 1. Testing Authentication ===")
    auth_resp = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": "demo@fraudlens.ai", "password": "FraudLens@2026"}
    )
    assert auth_resp.status_code == 200, f"Auth failed: {auth_resp.text}"
    token = auth_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("  Authenticated successfully. Token acquired.")

    print("\n=== 2. Testing Company Verification & Persistence ===")
    comp_resp = requests.post(
        f"{BASE_URL}/api/company/verify",
        headers=headers,
        json={"company_name": "TCS", "domain": "tcs.com"}
    )
    assert comp_resp.status_code == 200, f"Company verify failed: {comp_resp.text}"
    comp_data = comp_resp.json()["data"]
    inv_id = comp_data.get("investigation_id")
    print(f"  Company check returned status: {comp_data.get('company_status')}, investigation_id: {inv_id}")
    assert inv_id is not None, "investigation_id should not be None"

    print("\n=== 3. Testing PDF & JSON Report Downloads ===")
    pdf_resp = requests.get(
        f"{BASE_URL}/api/results/{inv_id}/download?format=pdf&token={token}"
    )
    assert pdf_resp.status_code == 200, f"PDF download failed with {pdf_resp.status_code}: {pdf_resp.text}"
    assert pdf_resp.headers.get("content-type") == "application/pdf"
    assert len(pdf_resp.content) > 1000, f"PDF file too small: {len(pdf_resp.content)} bytes"
    print(f"  PDF downloaded successfully ({len(pdf_resp.content)} bytes). Header: {pdf_resp.headers.get('content-type')}")

    json_resp = requests.get(
        f"{BASE_URL}/api/results/{inv_id}/download?format=json&token={token}"
    )
    assert json_resp.status_code == 200, f"JSON download failed: {json_resp.text}"
    json_data = json_resp.json()
    print(f"  JSON downloaded successfully. Type: {json_data.get('type')}, Risk: {json_data.get('risk_score')}")

    print("\n=== 4. Testing Multi-Image Upload (3 images at once) & Anomaly Detection ===")
    # Create 3 synthetic test screenshot images
    img1_bytes = io.BytesIO()
    im1 = Image.new("RGB", (400, 400), color=(240, 240, 240))
    d1 = ImageDraw.Draw(im1)
    d1.text((20, 50), "URGENT NOTICE: Pay 5000 INR immediately to avoid arrest.", fill=(255, 0, 0))
    d1.text((20, 100), "Send money to UPI: scammer@okaxis", fill=(0, 0, 0))
    im1.save(img1_bytes, format="PNG")
    img1_bytes.seek(0)

    img2_bytes = io.BytesIO()
    im2 = Image.new("RGB", (400, 400), color=(255, 255, 240))
    d2 = ImageDraw.Draw(im2)
    d2.text((20, 50), "Bank Verification: Share OTP to claim 100,000 lottery winnings.", fill=(200, 0, 0))
    im2.save(img2_bytes, format="PNG")
    img2_bytes.seek(0)

    img3_bytes = io.BytesIO()
    im3 = Image.new("RGB", (400, 400), color=(245, 245, 255))
    d3 = ImageDraw.Draw(im3)
    d3.text((20, 50), "Fake receipt confirmation: Paid successfully 10,000", fill=(0, 150, 0))
    im3.save(img3_bytes, format="PNG")
    img3_bytes.seek(0)

    files = [
        ("files", ("screenshot1.png", img1_bytes.getvalue(), "image/png")),
        ("files", ("screenshot2.png", img2_bytes.getvalue(), "image/png")),
        ("files", ("screenshot3.png", img3_bytes.getvalue(), "image/png")),
    ]
    data = {"context": "Suspected lottery and payment extortion messages"}

    img_resp = requests.post(
        f"{BASE_URL}/api/scam/image-analysis",
        headers=headers,
        files=files,
        data=data
    )
    assert img_resp.status_code == 200, f"Image analysis failed: {img_resp.text}"
    img_result = img_resp.json()["data"]
    print(f"  Multi-image analysis mode: {img_result.get('analysis_mode')}")
    print(f"  Images processed: {img_result.get('images_analyzed')}")
    print(f"  Risk score: {img_result.get('risk_score')}, Level: {img_result.get('risk_level')}")
    print(f"  Anomalies detected: {img_result.get('anomalies_detected')}")
    assert img_result.get("images_analyzed") == 3, f"Expected 3 images, got {img_result.get('images_analyzed')}"
    assert img_result.get("investigation_id") is not None, "investigation_id should be present"

    # Test downloading PDF report for multimodal image analysis
    img_inv_id = img_result.get("investigation_id")
    img_pdf_resp = requests.get(
        f"{BASE_URL}/api/results/{img_inv_id}/download?format=pdf&token={token}"
    )
    assert img_pdf_resp.status_code == 200, f"Multi-image PDF download failed: {img_pdf_resp.text}"
    assert len(img_pdf_resp.content) > 1000
    print(f"  Multi-image PDF report generated and downloaded successfully ({len(img_pdf_resp.content)} bytes)!")

    print("\n=== 5. Testing ML Model Transaction Inference & UPI Report Download ===")
    with open("fraudlens-backend/datasets/sample_transactions.csv", "rb") as f:
        csv_bytes = f.read()

    tx_resp = requests.post(
        f"{BASE_URL}/api/transactions/analyze",
        headers=headers,
        files={"file": ("sample_transactions.csv", csv_bytes, "text/csv")}
    )
    assert tx_resp.status_code == 200, f"Transaction analyze failed: {tx_resp.text}"
    tx_data = tx_resp.json()["data"]
    tx_results = tx_data.get("transactions", [])
    print(f"  ML analyzed {len(tx_results)} transaction(s). Overall risk: {tx_data.get('risk_score')}/100, Tier: {tx_data.get('risk_level')}")
    assert len(tx_results) > 0, "Expected transaction results"
    for t in tx_results[-2:]: # Look at the two fraud test cases
        print(f"    Txn {t.get('transaction_id')}: Amount={t.get('amount')}, FraudProb={t.get('fraud_probability')}, Anomaly={t.get('is_anomalous')}, Signals={t.get('signals')}")
        assert t.get('fraud_probability') >= 0.5 or t.get('is_anomalous') == 1, "Fraud cases should be flagged"

    upi_inv_id = tx_data.get("investigation_id")
    print(f"  UPI Investigation ID: {upi_inv_id}")
    upi_pdf_resp = requests.get(
        f"{BASE_URL}/api/results/{upi_inv_id}/download?format=pdf&token={token}"
    )
    assert upi_pdf_resp.status_code == 200, f"UPI PDF download failed: {upi_pdf_resp.text}"
    print(f"  UPI PDF report downloaded successfully ({len(upi_pdf_resp.content)} bytes)!")

    print("\n[SUCCESS] ALL TESTS PASSED WITH 100% SUCCESS!")

if __name__ == "__main__":
    test_full_pipeline()
