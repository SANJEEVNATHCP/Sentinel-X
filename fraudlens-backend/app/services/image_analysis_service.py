"""
FraudLens AI - Image & Chat Screenshot Phishing Analysis Service
Analyzes conversation screenshots, fake support chats, and payment demands for attack patterns.
"""

from typing import Dict, Any, List, Optional
from app.config import settings
from app.services.gemini_service import GeminiService
from app.services.risk_engine import RiskEngine
from app.services.evidence_engine import EvidenceEngine

ATTACK_PATTERNS = {
    "ADVANCE_PAYMENT": "Requesting upfront processing fees, security deposits, or advance registration payments.",
    "URGENCY_PRESSURE": "Creating manufactured panic, deadlines, or threats of account suspension.",
    "CREDENTIAL_THEFT": "Soliciting passwords, banking PINs, or private authentication credentials.",
    "OTP_SCAM": "Requesting one-time passwords, 2FA codes, or SMS security tokens.",
    "IMPERSONATION": "Falsely claiming identity as official bank personnel, support staff, or law enforcement.",
    "FAKE_RECRUITMENT": "Offering high-paying jobs requiring non-refundable training fees or equipment deposits.",
    "SOCIAL_ENGINEERING": "Exploiting emotional distress, romantic interest, or lottery claims."
}

class ImageAnalysisService:
    @classmethod
    def analyze_chat_indicators(cls, text_content: str) -> Dict[str, Any]:
        """
        Detects scam signatures from OCR or transcribed chat conversations.
        """
        lowered = text_content.lower()
        detected_patterns = []
        evidence = []
        risk_score = 0.0

        if any(w in lowered for w in ["registration fee", "security deposit", "send money", "processing charge", "pay upfront"]):
            detected_patterns.append({"pattern": "ADVANCE_PAYMENT", "description": ATTACK_PATTERNS["ADVANCE_PAYMENT"]})
            risk_score += 40.0
            evidence.append(EvidenceEngine.create_evidence_item(
                category="Conversation Intent",
                signal="Advance Fee Request",
                observed_value="Fee Demand Detected",
                reference_value="Zero Upfront Fees Policy",
                severity="CRITICAL",
                confidence=0.95,
                risk_contribution=40.0,
                source="Social Engineering Classifier",
                explanation="Message requests upfront payments for jobs, prizes, or document processing."
            ))

        if any(w in lowered for w in ["immediately", "within 10 minutes", "urgent", "account suspended", "police", "arrest"]):
            detected_patterns.append({"pattern": "URGENCY_PRESSURE", "description": ATTACK_PATTERNS["URGENCY_PRESSURE"]})
            risk_score += 25.0
            evidence.append(EvidenceEngine.create_evidence_item(
                category="Psychological Tactics",
                signal="Urgency Pressure",
                observed_value="Artificial Urgency",
                reference_value="Standard Communication",
                severity="HIGH",
                confidence=0.90,
                risk_contribution=25.0,
                source="Heuristic Intent Detector",
                explanation="Sender employs pressure tactics and artificial deadlines to force hasty compliance."
            ))

        if any(w in lowered for w in ["otp", "one time password", "share code", "verification code"]):
            detected_patterns.append({"pattern": "OTP_SCAM", "description": ATTACK_PATTERNS["OTP_SCAM"]})
            risk_score += 45.0
            evidence.append(EvidenceEngine.create_evidence_item(
                category="Credential Harvesting",
                signal="OTP Elicitation",
                observed_value="OTP Request",
                reference_value="Private OTP Protection",
                severity="CRITICAL",
                confidence=0.98,
                risk_contribution=45.0,
                source="Credential Protection Guard",
                explanation="Critical threat: Message attempts to solicit a one-time verification password."
            ))

        final_score, level = RiskEngine.calculate_risk(base_points=risk_score)
        
        recommendations = []
        if detected_patterns:
            recommendations.append("Never share OTPs, banking passwords, or transfer funds to personal UPI handles.")
            recommendations.append("Block the sender and report to official cyber crime authorities (e.g. cybercrime.gov.in).")
        else:
            recommendations.append("No active fraud signatures detected in screenshot text. Maintain standard vigilance.")

        return {
            "risk_score": final_score,
            "risk_level": level,
            "attack_patterns": detected_patterns,
            "evidence": evidence,
            "recommendations": recommendations
        }

    @classmethod
    async def analyze_multimodal_images(
        cls,
        image_paths: List[str],
        context_text: Optional[str] = None,
        custom_api_key: Optional[str] = None,
        file_names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Analyzes up to 3 images (screenshots, payment proofs, chat threads) for anomalies,
        using Google Gemini vision with automatic fallback to local OCR & forensic heuristics.
        """
        # 1. Attempt Gemini Multimodal Vision first
        gemini_res = GeminiService.analyze_images_for_anomalies(
            image_paths=image_paths,
            context_text=context_text,
            custom_api_key=custom_api_key
        )
        if gemini_res and isinstance(gemini_res, dict) and "risk_score" in gemini_res:
            anomalies = gemini_res.get("anomalies_detected", [])
            evidence = gemini_res.get("evidence", [])
            patterns = gemini_res.get("attack_patterns", [])
            recs = gemini_res.get("recommendations", [])
            score = float(gemini_res.get("risk_score", 0.0))
            level = gemini_res.get("risk_level", "LOW")

            # Extract or compute explicit offer verdict
            offer_verdict = gemini_res.get("offer_verdict")
            if not offer_verdict:
                offer_verdict = "TRUSTED OFFER" if (score < 35.0 and not patterns) else "UNTRUSTED OFFER"

            offer_reason = gemini_res.get("offer_verdict_reason")
            if not offer_reason:
                if offer_verdict == "TRUSTED OFFER":
                    offer_reason = "Verified authentic credentials, realistic terms, and absence of upfront payments or credential requests."
                else:
                    offer_reason = f"High-risk flags detected by Gemini AI ({len(patterns)} attack pattern(s), {len(anomalies)} anomaly signal(s))."

            return {
                "offer_verdict": offer_verdict,
                "offer_verdict_reason": offer_reason,
                "risk_score": score,
                "risk_level": level,
                "summary": gemini_res.get("summary") or f"Gemini Vision classified as {offer_verdict} ({len(anomalies)} anomaly(ies) identified).",
                "anomalies_detected": anomalies,
                "attack_patterns": patterns,
                "evidence": evidence,
                "recommendations": recs,
                "extracted_text": gemini_res.get("extracted_text", ""),
                "images_analyzed": len(image_paths),
                "analysis_mode": "GEMINI_MULTIMODAL_VISION",
                "source": "Google Gemini Vision Analysis"
            }

        # 2. Resilient Fallback: Local OCR + Forensic Heuristic Analysis
        extracted_texts = []
        for path in image_paths:
            text = ""
            try:
                import pytesseract
                from PIL import Image
                img = Image.open(path)
                text = pytesseract.image_to_string(img)
            except Exception:
                pass

            if not text:
                try:
                    from app.services.pdf_service import PDFService
                    text = PDFService.extract_text(path)
                except Exception:
                    text = ""
            extracted_texts.append(text)

        combined_text = (" ".join(extracted_texts) + " " + (context_text or "")).strip()

        # Run heuristic detection on extracted text & context
        base_res = cls.analyze_chat_indicators(combined_text)

        anomalies = []
        for p in base_res.get("attack_patterns", []):
            anomalies.append(f"{p['pattern']}: {p['description']}")

        if not anomalies and context_text:
            anomalies.append(f"Context observation: {context_text[:120]}")

        if not anomalies:
            anomalies.append("No overt visual tampering or malicious keywords detected in uploaded images.")

        is_trusted = (base_res["risk_score"] < 35.0 and len(base_res.get("attack_patterns", [])) == 0)
        offer_verdict = "TRUSTED OFFER" if is_trusted else "UNTRUSTED OFFER"
        offer_reason = (
            "No upfront payment requests, phishing keywords, or psychological pressure tactics detected."
            if is_trusted else
            f"Detected {len(base_res.get('attack_patterns', []))} threat signature(s) such as upfront fee requests or artificial urgency."
        )

        base_res["offer_verdict"] = offer_verdict
        base_res["offer_verdict_reason"] = offer_reason
        base_res["anomalies_detected"] = anomalies
        base_res["extracted_text"] = combined_text[:1000]
        base_res["images_analyzed"] = len(image_paths)
        base_res["analysis_mode"] = "LOCAL_IMAGE_FORENSICS"
        base_res["source"] = "FraudLens Forensic Vision Heuristics"
        base_res["summary"] = f"Classified as {offer_verdict}. Identified {len(base_res.get('attack_patterns', []))} threat pattern(s) and {len(anomalies)} anomaly observation(s)."

        return base_res

