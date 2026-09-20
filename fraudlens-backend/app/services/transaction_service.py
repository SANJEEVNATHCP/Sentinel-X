"""
FraudLens AI - UPI Transaction Service
Ingests CSV/XLSX, derives behavioral profiles, executes dual ML models, and generates evidence.
"""

import io
import pandas as pd
from typing import Dict, Any, List
from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.exceptions import FileProcessingError
from app.ml.feature_engineering import extract_transaction_features
from app.services.behavioral_service import BehavioralService
from app.services.fraud_model_service import FraudModelService
from app.services.anomaly_service import AnomalyService
from app.services.risk_engine import RiskEngine
from app.services.evidence_engine import EvidenceEngine
from app.models.investigation import Investigation
from app.models.investigation_result import InvestigationResult
from app.models.evidence import Evidence
from app.models.risk_factor import RiskFactor
from app.models.transaction import TransactionBatch, Transaction as TransactionModel
from app.utils.timestamps import utc_now_iso

class TransactionService:
    @classmethod
    async def process_transaction_file(
        cls,
        db: Session,
        user_id: str,
        file: UploadFile,
        investigation_id: str
    ) -> Dict[str, Any]:
        """Parses CSV or Excel transaction sheet, runs feature engineering and ML risk engine."""
        filename = file.filename or ""
        content = await file.read()
        
        try:
            if filename.endswith(".csv"):
                df = pd.read_csv(io.BytesIO(content))
            elif filename.endswith((".xlsx", ".xls")):
                df = pd.read_excel(io.BytesIO(content))
            else:
                raise FileProcessingError("File must be a CSV or XLSX spreadsheet")
        except Exception as e:
            raise FileProcessingError(f"Spreadsheet could not be parsed: {str(e)}")

        if len(df) == 0:
            raise FileProcessingError("Uploaded transaction file contains no data rows")

        # Extract features and calculate receiver frequency
        processed_df = extract_transaction_features(df)
        
        # Calculate receiver frequency distribution across the batch
        receiver_counts = {}
        for _, r in processed_df.iterrows():
            r_key = str(r.get("receiver_id") or r.get("receiver") or r.get("upi_id") or r.get("beneficiary_id") or "Unknown").strip()
            if r_key:
                receiver_counts[r_key] = receiver_counts.get(r_key, 0) + 1

        amounts = [float(a) for a in processed_df["amount"].tolist()]
        # Filter outliers for an accurate baseline
        if len(amounts) > 2:
            import numpy as np
            q75 = float(np.percentile(amounts, 75))
            baseline_amts = [a for a in amounts if a <= max(q75 * 1.6, 5000.0)]
            if not baseline_amts:
                baseline_amts = amounts
        else:
            baseline_amts = amounts

        user_profile = BehavioralService.calculate_user_profile(baseline_amts)
        user_mean = round(user_profile["mean"], 2) if user_profile["mean"] > 0 else round(float(sum(amounts) / len(amounts)), 2)
        user_std = round(user_profile["std"], 2) if user_profile["std"] > 0 else 1.0

        transactions_data = []
        high_risk_count = 0
        all_evidence = []
        all_risk_factors = []
        max_txn_risk = 0.0

        for idx, row in processed_df.iterrows():
            amt = float(row["amount"])
            dev = BehavioralService.evaluate_transaction_deviation(amt, user_mean, user_std)
            ratio = round(dev["ratio"], 2)
            failed = int(row.get("failed_attempts", 0))
            is_night = int(row.get("is_night_txn", 0))
            hour = int(row.get("hour", 12))
            day_of_week = int(row.get("day_of_week", 0))

            # Identify receiver ID
            receiver_id = str(row.get("receiver_id") or row.get("receiver") or row.get("upi_id") or row.get("beneficiary_id") or f"REC_{idx+1}").strip()
            freq = receiver_counts.get(receiver_id, 1)

            # Location deviation: flag known high-risk regions
            raw_location = str(row.get("location", "")).lower().strip()
            loc_dev = 0.85 if raw_location in {"lagos", "foreign", "unknown", "vpn", "nigeria", "ghana", "abroad"} else 0.05

            # Derived flag features — mirrors app/ml/ml/features.py logic exactly
            unusual_hour_flag = 1.0 if hour in {0, 1, 2, 3, 4, 5} else 0.0
            high_velocity_flag = 1.0 if freq >= 5 else 0.0
            high_amount_flag = 1.0 if ratio >= 4.0 else 0.0

            # Full 15-feature vector for XGBoost (matches training feature order)
            features = {
                # Core numeric features
                "amount": amt,
                "transaction_hour": float(hour),
                "day_of_week": float(day_of_week),
                "transaction_frequency": float(freq),
                "avg_amount": float(user_mean),
                "amount_deviation": ratio,
                "transactions_previous_hour": float(freq),
                "beneficiary_count": float(freq),
                "previous_fraud_alerts": float(failed),       # reused: failed attempts as proxy
                "is_new_device": float(1 if raw_location not in {"mumbai", "delhi", "bangalore", "chennai", "hyderabad", "kolkata"} and loc_dev > 0.5 else 0),
                "is_new_beneficiary": 0.0,                    # not available from CSV; default safe
                "location_deviation": loc_dev,
                "unusual_hour_flag": unusual_hour_flag,
                "high_velocity_flag": high_velocity_flag,
                "high_amount_flag": high_amount_flag,
                # Legacy keys kept for AnomalyService / heuristic fallback
                "amount_ratio": ratio,
                "hour": float(hour),
                "frequency": float(freq),
                "failed_attempts": float(failed),
                "is_night_txn": float(is_night),
                "baseline_mean": float(user_mean),
            }

            # 1. Supervised Fraud Probability — XGBoost (xgboost_fraud_model.joblib)
            fraud_prob = FraudModelService.predict_fraud_probability(features)

            # 2. Unsupervised Anomaly Detection via Isolation Forest ('isolate frost' method)
            anomaly_res = AnomalyService.detect_anomaly(features)
            anom_score = anomaly_res["anomaly_score"]
            is_anom = anomaly_res["is_anomalous"]

            # 3. Baseline Explanation: "What goes wrong"
            wrong_signals = []
            if ratio >= 4.0:
                wrong_signals.append(f"Amount ₹{amt:,.2f} is {ratio:.1f}x higher than user baseline average of ₹{user_mean:,.2f}")
            elif ratio <= 0.15 and amt > 0:
                wrong_signals.append(f"Amount ₹{amt:,.2f} is unusually low compared to baseline average ₹{user_mean:,.2f}")

            if freq >= 2:
                wrong_signals.append(f"Receiver velocity spike ({freq} transactions directed to {receiver_id})")

            if is_night:
                wrong_signals.append(f"Unusual off-hours transaction at {hour:02d}:00")

            if failed >= 2:
                wrong_signals.append(f"Preceded by {failed} consecutive failed authorization attempts")

            if is_anom:
                wrong_signals.append(f"Flagged as behavioral anomaly by Isolation Forest (score: {anom_score:.4f})")

            if wrong_signals:
                what_went_wrong = "; ".join(wrong_signals) + "."
            else:
                what_went_wrong = f"Normal transaction: Amount aligns with baseline (₹{amt:,.2f} vs average ₹{user_mean:,.2f}); standard receiver frequency ({freq}); Daytime timing; Verified normal by Isolation Forest."

            # 4. Rule Engine Points
            row_points = 0.0
            row_signals = []

            if ratio >= 15.0:
                row_points += 35.0
                row_signals.append(f"Critical Amount Spike ({ratio}x user baseline)")
                all_evidence.append(EvidenceEngine.create_evidence_item(
                    category="Transaction Behavior",
                    signal="Amount Anomaly",
                    observed_value=f"₹{amt:,.2f}",
                    reference_value=f"User average ₹{user_mean:,.2f}",
                    severity="CRITICAL",
                    confidence=0.96,
                    risk_contribution=35.0,
                    source="Isolation Forest & Behavioral Profiler",
                    explanation=f"Transaction amount is {ratio}x higher than the user baseline average of ₹{user_mean:,.2f}."
                ))
            elif ratio >= 4.0:
                row_points += 20.0
                row_signals.append(f"Significant Amount Anomaly ({ratio}x baseline)")
                all_evidence.append(EvidenceEngine.create_evidence_item(
                    category="Transaction Behavior",
                    signal="Amount Anomaly",
                    observed_value=f"₹{amt:,.2f}",
                    reference_value=f"User average ₹{user_mean:,.2f}",
                    severity="HIGH",
                    confidence=0.92,
                    risk_contribution=20.0,
                    source="Isolation Forest & Behavioral Profiler",
                    explanation=f"Transaction amount departs from baseline average by {ratio}x."
                ))

            if freq >= 3:
                row_points += 20.0
                row_signals.append(f"High Receiver Frequency ({freq} txns to {receiver_id})")

            if failed >= 2:
                row_points += 20.0
                row_signals.append(f"Repeated Failed Attempts ({failed} retries)")
                all_evidence.append(EvidenceEngine.create_evidence_item(
                    category="Authentication & Device",
                    signal="Velocity Anomaly",
                    observed_value=f"{failed} failed attempts",
                    reference_value="0 failed attempts",
                    severity="HIGH",
                    confidence=0.90,
                    risk_contribution=20.0,
                    source="UPI Gateway Records",
                    explanation=f"Transaction preceded by {failed} consecutive authorization failures."
                ))

            if is_night:
                row_points += 15.0
                row_signals.append(f"Unusual Off-Hours Transaction ({hour:02d}:00)")

            if is_anom:
                row_points += 20.0
                row_signals.append(f"Isolation Forest Anomaly Flagged (Score: {anom_score})")

            if fraud_prob >= 0.70:
                row_points += 25.0
            elif fraud_prob >= 0.40:
                row_points += 15.0

            total_row_score = min(max(row_points, 0.0), 100.0)
            if total_row_score >= 65.0 or is_anom:
                high_risk_count += 1

            if total_row_score > max_txn_risk:
                max_txn_risk = total_row_score

            transactions_data.append({
                "transaction_id": str(row.get("transaction_id", f"TXN_{idx+1}")),
                "amount": amt,
                "timestamp": str(row.get("timestamp", "")),
                "sender": str(row.get("sender", "")),
                "receiver": str(row.get("receiver", "")),
                "receiver_id": receiver_id,
                "upi_id": str(row.get("upi_id", "")),
                "device_id": str(row.get("device_id", "")),
                "location": str(row.get("location", "")),
                "frequency": freq,
                "baseline_mean": user_mean,
                "amount_ratio": ratio,
                "what_went_wrong": what_went_wrong,
                # XGBoost model output
                "xgboost_score": fraud_prob,
                "model_used": "XGBoost (xgboost_fraud_model.joblib)",
                # Legacy alias kept for frontend backward compatibility
                "fraud_probability": fraud_prob,
                # Isolation Forest output
                "anomaly_score": anom_score,
                "is_anomalous": is_anom,
                "signals": row_signals
            })

        # Calculate Overall Investigation Risk Score
        overall_score, overall_level = RiskEngine.calculate_risk(base_points=max_txn_risk)

        if high_risk_count > 0:
            all_risk_factors.append({
                "name": "High-Risk Transaction Outliers",
                "weight": 1.0,
                "contribution": 35.0,
                "description": f"{high_risk_count} transaction(s) exhibited severe behavioral divergence."
            })

        recommendations = []
        if overall_level in ["HIGH_RISK", "SUSPICIOUS"]:
            recommendations.append("Immediately verify recent high-value UPI payments with your issuing bank.")
            recommendations.append("Place a temporary block or cooling period on unverified beneficiaries.")
        else:
            recommendations.append("Transactions align within typical behavioral parameters. Continue normal monitoring.")

        summary_text = (
            f"Analyzed {len(transactions_data)} transactions against historical average of ₹{user_mean:,.2f}. "
            f"Detected {high_risk_count} transaction(s) with high behavioral anomaly indicators."
        )

        ai_summary = (
            f"FraudLens behavioral analysis flagged {high_risk_count} unusual payment pattern(s). "
            f"The primary risk driver is sudden high-value amounts departing significantly from the historical baseline."
            if high_risk_count > 0 else
            "All inspected transactions operate within expected baseline thresholds with no velocity spikes."
        )

        # Update Investigation Record
        inv = db.query(Investigation).filter(Investigation.id == investigation_id).first()
        if inv:
            inv.status = "COMPLETED"
            inv.risk_score = overall_score
            inv.risk_level = overall_level
            inv.summary = summary_text

            # Save Batch
            batch = TransactionBatch(
                investigation_id=investigation_id,
                total_transactions=len(transactions_data),
                user_historical_mean=user_mean,
                user_historical_std=user_std,
                high_risk_count=high_risk_count,
                summary_json={"recommendations": recommendations}
            )
            db.add(batch)
            db.flush()

            for t in transactions_data:
                txn_m = TransactionModel(
                    batch_id=batch.id,
                    transaction_id=t["transaction_id"],
                    amount=t["amount"],
                    sender=t["sender"],
                    receiver=t["receiver"],
                    upi_id=t["upi_id"],
                    device_id=t["device_id"],
                    location=t["location"],
                    fraud_probability=t["fraud_probability"],
                    anomaly_score=t["anomaly_score"],
                    is_anomalous=t["is_anomalous"]
                )
                db.add(txn_m)

            for ev in all_evidence[:10]: # Store top evidence
                e_obj = Evidence(
                    investigation_id=investigation_id,
                    category=ev["category"],
                    signal=ev["signal"],
                    observed_value=ev["observed_value"],
                    reference_value=ev["reference_value"],
                    severity=ev["severity"],
                    confidence=ev["confidence"],
                    risk_contribution=ev["risk_contribution"],
                    source=ev["source"],
                    explanation=ev["explanation"]
                )
                db.add(e_obj)

            for rf in all_risk_factors:
                rf_obj = RiskFactor(
                    investigation_id=investigation_id,
                    name=rf["name"],
                    weight=rf["weight"],
                    contribution=rf["contribution"],
                    description=rf["description"]
                )
                db.add(rf_obj)

            # Create persistent InvestigationResult
            inv_res = InvestigationResult(
                investigation_id=investigation_id,
                user_id=user_id,
                type="UPI",
                risk_score=overall_score,
                risk_level=overall_level,
                summary=summary_text,
                recommendation="; ".join(recommendations),
                evidence_json=all_evidence,
                risk_factors_json=all_risk_factors,
                verification_json={"user_mean": user_mean, "user_std": user_std},
                attack_patterns_json=[],
                ai_summary=ai_summary,
                transactions_json=transactions_data  # XGBoost per-transaction scores
            )
            db.add(inv_res)
            db.commit()

        return {
            "investigation_id": investigation_id,
            "total_transactions": len(transactions_data),
            "user_historical_mean": user_mean,
            "user_historical_std": user_std,
            "high_risk_count": high_risk_count,
            "risk_score": overall_score,
            "risk_level": overall_level,
            "summary": summary_text,
            "evidence": all_evidence,
            "risk_factors": all_risk_factors,
            "recommendations": recommendations,
            "ai_summary": ai_summary,
            "created_at": utc_now_iso(),
            "transactions": transactions_data
        }
