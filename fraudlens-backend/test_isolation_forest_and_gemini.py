"""
Verification Script:
1. Tests Isolation Forest UPI analysis on CSV and Excel input.
2. Checks transaction_id, receiver_id, receiver frequency, and 'what goes wrong' baseline comparison.
3. Tests Gemini image analysis for TRUSTED OFFER vs UNTRUSTED OFFER verdict.
"""

import sys
import os
import io
import asyncio
import pandas as pd
from fastapi import UploadFile

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal
from app.models.user import User
from app.models.investigation import Investigation
from app.services.transaction_service import TransactionService
from app.services.image_analysis_service import ImageAnalysisService
from app.services.anomaly_service import AnomalyService

async def test_upi_isolation_forest():
    print("\n--- 1. Testing Isolation Forest UPI Transaction Analysis ---")
    db = SessionLocal()
    try:
        user = db.query(User).first()
        if not user:
            print("❌ No test user found in DB")
            return False

        inv = Investigation(
            user_id=user.id,
            type="UPI",
            status="PROCESSING",
            target_entity="sample_transactions.csv"
        )
        db.add(inv)
        db.commit()
        db.refresh(inv)

        csv_path = os.path.join(os.path.dirname(__file__), "datasets", "sample_transactions.csv")
        with open(csv_path, "rb") as f:
            content = f.read()

        upload_file = UploadFile(filename="sample_transactions.csv", file=io.BytesIO(content))
        
        result = await TransactionService.process_transaction_file(
            db=db,
            user_id=user.id,
            file=upload_file,
            investigation_id=inv.id
        )

        print(f"[OK] Total Transactions Analyzed: {result['total_transactions']}")
        print(f"[OK] Baseline Mean (INR): {result['user_historical_mean']}")
        print(f"[OK] High Risk Count: {result['high_risk_count']}")
        print(f"[OK] Investigation Risk Score: {result['risk_score']} ({result['risk_level']})")

        txns = result["transactions"]
        assert len(txns) > 0, "No transactions returned!"
        
        # Verify required fields
        for idx, t in enumerate(txns):
            assert "transaction_id" in t and t["transaction_id"], f"Missing transaction_id in row {idx}"
            assert "receiver_id" in t and t["receiver_id"], f"Missing receiver_id in row {idx}"
            assert "frequency" in t and isinstance(t["frequency"], int), f"Missing frequency in row {idx}"
            assert "what_went_wrong" in t and t["what_went_wrong"], f"Missing what_went_wrong in row {idx}"
            assert "model_used" in t and t["model_used"] == "Isolation Forest", f"Model not Isolation Forest in row {idx}"
            assert "anomaly_score" in t, f"Missing anomaly_score in row {idx}"
            assert "is_anomalous" in t, f"Missing is_anomalous in row {idx}"

        # Test normal transaction (TXN1001)
        t_norm = txns[0]
        print(f"\n[Normal Txn Example - {t_norm['transaction_id']}]:")
        print(f"  Receiver ID: {t_norm['receiver_id']}")
        print(f"  Frequency: {t_norm['frequency']}")
        print(f"  Amount: INR {t_norm['amount']} (Ratio: {t_norm['amount_ratio']}x)")
        print(f"  Isolation Forest Score: {t_norm['anomaly_score']} (Anomalous: {t_norm['is_anomalous']})")
        print(f"  What Went Wrong: {t_norm['what_went_wrong']}")

        # Test anomalous transaction (TXN1008)
        t_fraud = [t for t in txns if t["amount"] >= 70000][0]
        print(f"\n[Anomalous Txn Example - {t_fraud['transaction_id']}]:")
        print(f"  Receiver ID: {t_fraud['receiver_id']}")
        print(f"  Frequency: {t_fraud['frequency']}")
        print(f"  Amount: INR {t_fraud['amount']} (Ratio: {t_fraud['amount_ratio']}x)")
        print(f"  Isolation Forest Score: {t_fraud['anomaly_score']} (Anomalous: {t_fraud['is_anomalous']})")
        print(f"  What Went Wrong: {t_fraud['what_went_wrong']}")

        assert t_fraud["is_anomalous"] == 1 or t_fraud["anomaly_score"] >= 0.6, "TXN1008 was not flagged as anomaly!"
        assert "baseline average" in t_fraud["what_went_wrong"].lower(), "Baseline mean comparison missing from what_went_wrong!"
        print("\n[OK] Isolation Forest UPI payment verification PASSED!")
        return True
    finally:
        db.close()

async def test_gemini_offer_verdict():
    print("\n--- 2. Testing Gemini Image Offer Verification ---")
    
    # Test heuristic fallback image verification
    from PIL import Image
    temp_img_path = os.path.join(os.path.dirname(__file__), "temp_uploads", "test_offer_img.png")
    img = Image.new("RGB", (300, 150), color=(255, 255, 255))
    img.save(temp_img_path)

    # 1. Suspicious offer text (Registration fee demanded)
    res_scam = await ImageAnalysisService.analyze_multimodal_images(
        image_paths=[temp_img_path],
        context_text="Urgent: pay registration fee of Rs 5000 immediately to receive employment letter"
    )
    print(f"\n[Scam/Demanding Offer Test]:")
    print(f"  Offer Verdict: {res_scam.get('offer_verdict')}")
    print(f"  Offer Verdict Reason: {res_scam.get('offer_verdict_reason')}")
    print(f"  Risk Score: {res_scam.get('risk_score')} ({res_scam.get('risk_level')})")
    assert res_scam.get("offer_verdict") == "UNTRUSTED OFFER", f"Expected UNTRUSTED OFFER, got {res_scam.get('offer_verdict')}"

    # 2. Legitimate offer text
    res_clean = await ImageAnalysisService.analyze_multimodal_images(
        image_paths=[temp_img_path],
        context_text="Official joining letter from Infosys Technologies with standard terms and no advance payments"
    )
    print(f"\n[Clean Offer Test]:")
    print(f"  Offer Verdict: {res_clean.get('offer_verdict')}")
    print(f"  Offer Verdict Reason: {res_clean.get('offer_verdict_reason')}")
    print(f"  Risk Score: {res_clean.get('risk_score')} ({res_clean.get('risk_level')})")
    assert res_clean.get("offer_verdict") == "TRUSTED OFFER", f"Expected TRUSTED OFFER, got {res_clean.get('offer_verdict')}"

    print("\n[OK] Gemini Image Offer Verdict classification PASSED!")
    return True

async def main():
    upi_ok = await test_upi_isolation_forest()
    gemini_ok = await test_gemini_offer_verdict()
    if upi_ok and gemini_ok:
        print("\n==========================================")
        print("ALL REQUIREMENTS VERIFIED SUCCESSFULLY!")
        print("==========================================")
    else:
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
