"""
FraudLens AI - Combined Multi-Signal Scam Service
Unifies URL scans, company dataset verification, and social engineering indicators into a single investigation.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.services.url_service import URLService
from app.services.company_service import CompanyService
from app.services.gemini_service import GeminiService
from app.models.investigation import Investigation
from app.models.investigation_result import InvestigationResult
from app.models.scam_analysis import ScamAnalysis
from app.models.evidence import Evidence
from app.models.risk_factor import RiskFactor
from app.utils.timestamps import utc_now_iso

class ScamService:
    @classmethod
    async def analyze_multi_signal(
        cls,
        db: Session,
        user_id: str,
        investigation_id: str,
        url: Optional[str] = None,
        company_name: Optional[str] = None,
        linkedin_url: Optional[str] = None,
        recruiter_email: Optional[str] = None,
        message_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Orchestrates multi-signal analysis combining URL scanning, company records,
        and linguistic intent indicators.
        """
        all_evidence = []
        all_risk_factors = []
        recommendations = []
        attack_patterns = []
        accumulated_risk = 0.0

        # 1. URL Analysis if provided
        url_res = None
        if url:
            url_res = await URLService.analyze_url(db, url)
            all_evidence.extend(url_res["evidence"])
            all_risk_factors.extend(url_res["risk_factors"])
            recommendations.extend(url_res["recommendations"])
            accumulated_risk += url_res["risk_score"]

        # 2. Company Verification if provided
        company_res = None
        if company_name:
            company_res = CompanyService.evaluate_company(
                db=db,
                company_name=company_name,
                domain=url,
                linkedin_url=linkedin_url,
                recruiter_email=recruiter_email
            )
            all_evidence.extend(company_res["evidence"])
            recommendations.extend(company_res["recommendations"])
            
            # If company is Inactive in master dataset, add high penalty
            if company_res["mca_result"]["is_inactive"]:
                accumulated_risk += 45.0
                all_risk_factors.append({
                    "name": "Inactive Company Threat",
                    "weight": 1.0,
                    "contribution": 45.0,
                    "description": "Company is flagged as INACTIVE in authoritative dataset."
                })
            elif not company_res["mca_result"]["is_active"]:
                accumulated_risk += 15.0

        # 3. Message/Chat Content Analysis
        if message_text:
            from app.services.image_analysis_service import ImageAnalysisService
            msg_res = ImageAnalysisService.analyze_chat_indicators(message_text)
            all_evidence.extend(msg_res["evidence"])
            attack_patterns.extend(msg_res["attack_patterns"])
            recommendations.extend(msg_res["recommendations"])
            accumulated_risk += msg_res["risk_score"]

        # Calculate Final Risk Clamped 0-100
        from app.services.risk_engine import RiskEngine
        final_score, final_level = RiskEngine.calculate_risk(base_points=accumulated_risk)

        summary_text = (
            f"Multi-signal investigation evaluated {1 if url else 0} URL(s) and "
            f"{1 if company_name else 0} company entity. Risk classification: {final_level} ({final_score}/100)."
        )

        ai_summary = GeminiService.generate_investigation_summary(
            analysis_type="SCAM_URL",
            risk_score=final_score,
            risk_level=final_level,
            evidence=all_evidence,
            recommendations=recommendations
        )

        # Store in Database
        inv = db.query(Investigation).filter(Investigation.id == investigation_id).first()
        if inv:
            inv.status = "COMPLETED"
            inv.risk_score = final_score
            inv.risk_level = final_level
            inv.summary = summary_text
            inv.target_entity = url or company_name or "Multi-Signal Target"

            scam_rec = ScamAnalysis(
                investigation_id=investigation_id,
                target_url=url,
                domain=url_res.get("domain") if url_res else None,
                dataset_found=url_res["local_dataset"]["dataset_found"] if url_res else False,
                dataset_status=url_res["local_dataset"]["status"] if url_res else "NOT_FOUND",
                virustotal_status=url_res["virustotal"]["scan_status"] if url_res else "UNAVAILABLE",
                virustotal_malicious=url_res["virustotal"]["malicious"] if url_res else 0,
                virustotal_suspicious=url_res["virustotal"]["suspicious"] if url_res else 0,
                attack_patterns=attack_patterns,
                signals_json={"url_analysis": url_res, "company_eval": company_res}
            )
            db.add(scam_rec)

            for ev in all_evidence[:12]:
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
                type="SCAM_URL",
                risk_score=final_score,
                risk_level=final_level,
                summary=summary_text,
                recommendation="; ".join(recommendations),
                evidence_json=all_evidence,
                risk_factors_json=all_risk_factors,
                verification_json={"company": company_res, "url": url_res},
                attack_patterns_json=attack_patterns,
                ai_summary=ai_summary
            )
            db.add(inv_res)
            db.commit()

        return {
            "investigation_id": investigation_id,
            "type": "SCAM_URL",
            "risk_score": final_score,
            "risk_level": final_level,
            "summary": summary_text,
            "attack_patterns": attack_patterns,
            "evidence": all_evidence,
            "risk_factors": all_risk_factors,
            "recommendations": list(set(recommendations)),
            "ai_summary": ai_summary,
            "created_at": utc_now_iso()
        }
