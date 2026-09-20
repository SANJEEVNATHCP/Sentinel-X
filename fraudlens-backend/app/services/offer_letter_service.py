"""
FraudLens AI - Offer Letter Verification Pipeline
End-to-end processing pipeline integrating document OCR, company dataset lookup,
recruiter checks, and content risk scoring.
"""

from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.services.pdf_service import PDFService
from app.services.gemini_service import GeminiService
from app.services.company_service import CompanyService
from app.services.image_analysis_service import ImageAnalysisService
from app.models.investigation import Investigation
from app.models.investigation_result import InvestigationResult
from app.models.offer_letter import OfferLetterVerification
from app.models.evidence import Evidence
from app.models.risk_factor import RiskFactor
from app.utils.timestamps import utc_now_iso

class OfferLetterService:
    @classmethod
    async def verify_offer_letter(
        cls,
        db: Session,
        user_id: str,
        investigation_id: str,
        file_path: str
    ) -> Dict[str, Any]:
        """
        Executes complete verification pipeline:
        1. Extract text from PDF/Image
        2. Gemini structured entity extraction
        3. Company Master Dataset verification (Active vs Inactive)
        4. Recruiter domain consistency analysis
        5. Content threat pattern analysis (fees, urgent language)
        6. Compute trust score & store persistent derived result
        """
        # 1. Text Extraction
        raw_text = PDFService.extract_text(file_path)

        # 2. Gemini Extraction (Only extraction, no verification claims)
        extracted = GeminiService.extract_offer_letter_data(raw_text)
        company_name = extracted.get("company_name") or "Unknown Company"
        recruiter_email = extracted.get("recruiter_email")

        # 3. Authoritative Company Dataset Verification
        company_eval = CompanyService.evaluate_company(
            db=db,
            company_name=company_name,
            domain=extracted.get("company_website"),
            recruiter_email=recruiter_email
        )

        # 4. Content Risk Analysis (Advance fees, urgency)
        content_eval = ImageAnalysisService.analyze_chat_indicators(raw_text)

        # 5. Aggregate Evidence
        evidence = company_eval["evidence"] + content_eval["evidence"]
        
        # Calculate Final Trust Score
        base_trust = company_eval["trust_score"]
        # Penalize if fee requests or scam patterns are present in letter
        if content_eval["attack_patterns"]:
            base_trust = max(0.0, base_trust - 35.0)

        trust_score = round(base_trust, 1)

        if trust_score >= 85:
            risk_level = "TRUSTED"
        elif trust_score >= 65:
            risk_level = "NEEDS_VERIFICATION"
        elif trust_score >= 40:
            risk_level = "SUSPICIOUS"
        else:
            risk_level = "LIKELY_SCAM"

        recommendations = company_eval["recommendations"] + content_eval["recommendations"]

        summary = (
            f"Evaluated offer letter for '{company_name}'. Entity status in MCA dataset: {company_eval['mca_result']['company_status']}. "
            f"Overall Trust Score: {trust_score}/100 ({risk_level})."
        )

        ai_summary = GeminiService.generate_investigation_summary(
            analysis_type="OFFER_LETTER",
            risk_score=100.0 - trust_score,
            risk_level=risk_level,
            evidence=evidence,
            recommendations=recommendations
        )

        # Store in Database
        inv = db.query(Investigation).filter(Investigation.id == investigation_id).first()
        if inv:
            inv.status = "COMPLETED"
            inv.risk_score = round(100.0 - trust_score, 1)
            inv.risk_level = risk_level
            inv.summary = summary
            inv.target_entity = company_name

            ol_record = OfferLetterVerification(
                investigation_id=investigation_id,
                company_name=company_name,
                company_website=extracted.get("company_website"),
                recruiter_name=extracted.get("recruiter_name"),
                recruiter_email=recruiter_email,
                job_role=extracted.get("job_role"),
                salary=extracted.get("salary"),
                mca_match_status=company_eval["mca_result"]["company_status"],
                trust_score=trust_score,
                extracted_fields=extracted,
                indicators=content_eval["attack_patterns"]
            )
            db.add(ol_record)

            for ev in evidence[:10]:
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

            # Persistent derived result
            inv_res = InvestigationResult(
                investigation_id=investigation_id,
                user_id=user_id,
                type="OFFER_LETTER",
                risk_score=round(100.0 - trust_score, 1),
                risk_level=risk_level,
                summary=summary,
                recommendation="; ".join(recommendations),
                evidence_json=evidence,
                risk_factors_json=[],
                verification_json=company_eval,
                attack_patterns_json=content_eval["attack_patterns"],
                ai_summary=ai_summary
            )
            db.add(inv_res)
            db.commit()

        is_trusted = (trust_score >= 65 and not content_eval["attack_patterns"])
        offer_verdict = "TRUSTED OFFER" if is_trusted else "UNTRUSTED OFFER"
        offer_verdict_reason = (
            f"Offer from '{company_name}' matches active corporate records and contains no fee demands or extortion patterns."
            if is_trusted else
            f"Offer flagged with high risk: Trust score {trust_score}/100 with suspicious patterns or unverified corporate identity."
        )

        return {
            "investigation_id": investigation_id,
            "offer_verdict": offer_verdict,
            "offer_verdict_reason": offer_verdict_reason,
            "extracted_data": extracted,
            "mca_match_status": company_eval["mca_result"]["company_status"],
            "trust_score": trust_score,
            "risk_level": risk_level,
            "attack_patterns": content_eval["attack_patterns"],
            "evidence": evidence,
            "risk_factors": [],
            "recommendations": recommendations,
            "ai_summary": ai_summary,
            "created_at": utc_now_iso()
        }
