"""
FraudLens AI - Master Company & Entity Intelligence Service
Integrates MCA dataset evaluation (Active vs Inactive), LinkedIn, website, and recruiter verification.
"""

from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from app.services.mca_service import MCAService
from app.services.linkedin_service import LinkedInService
from app.services.website_service import WebsiteService
from app.services.recruiter_service import RecruiterService

class CompanyService:
    @classmethod
    def evaluate_company(
        cls,
        db: Optional[Session],
        company_name: str,
        domain: Optional[str] = None,
        linkedin_url: Optional[str] = None,
        recruiter_email: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Orchestrates full corporate verification based on the authoritative MCA dataset.
        Flags Active (real) vs Inactive (fake/defunct) status and computes explainable Trust Score.
        """
        # 1. Authoritative MCA Dataset Evaluation
        mca_res = MCAService.verify_company(db, company_name, domain)
        official_domain = mca_res.get("official_domain") or domain

        # 2. LinkedIn Verification
        linkedin_res = LinkedInService.verify_company_presence(linkedin_url, company_name) if linkedin_url else {
            "linkedin_found": False,
            "verification_status": "UNVERIFIED",
            "verification_message": "No LinkedIn URL provided for evaluation."
        }

        # 3. Website Verification
        website_res = WebsiteService.verify_website(official_domain) if official_domain else {
            "website_verified": False,
            "ssl_valid": False,
            "domain_exists": False,
            "message": "No domain available for website check."
        }

        # 4. Recruiter Verification
        recruiter_res = RecruiterService.verify_recruiter_email(recruiter_email, official_domain) if recruiter_email else {
            "email_verified": False,
            "domain_match": None,
            "free_email": False,
            "message": "No recruiter email provided for verification."
        }

        # 5. Trust Score Computation
        # Base Points Allocation
        mca_score = 0.0
        linkedin_score = 0.0
        website_score = 0.0
        recruiter_score = 0.0
        security_score = 15.0 # Default neutral

        evidence = []
        recommendations = []

        # MCA Component (30 pts max)
        if mca_res["is_active"]:
            mca_score = 30.0
            evidence.append({
                "category": "Corporate Registration",
                "signal": "MCA Master Dataset Status",
                "observed_value": "Active",
                "reference_value": "Registered MCA Enterprise",
                "severity": "LOW",
                "confidence": 1.0,
                "risk_contribution": 0.0,
                "source": "Ministry of Corporate Affairs (MCA) Dataset",
                "explanation": f"Entity '{mca_res['company_name']}' is confirmed ACTIVE with CIN: {mca_res['cin']} under {mca_res['roc']}."
            })
        elif mca_res["is_inactive"]:
            mca_score = 0.0
            evidence.append({
                "category": "Corporate Registration",
                "signal": "MCA Master Dataset Status",
                "observed_value": "Inactive",
                "reference_value": "Active Registered Enterprise",
                "severity": "CRITICAL",
                "confidence": 1.0,
                "risk_contribution": 45.0,
                "source": "Ministry of Corporate Affairs (MCA) Dataset",
                "explanation": f"ALERT: Company '{mca_res['company_name']}' is listed as INACTIVE / Defunct in dataset. Entity may be unauthorized."
            })
            recommendations.append("Entity is marked INACTIVE in corporate registers. Cease commercial or employment transactions.")
        else:
            mca_score = 10.0 # Unverified, don't zero out completely
            evidence.append({
                "category": "Corporate Registration",
                "signal": "MCA Master Dataset Status",
                "observed_value": "NOT_FOUND",
                "reference_value": "Registered MCA Enterprise",
                "severity": "MEDIUM",
                "confidence": 0.85,
                "risk_contribution": 15.0,
                "source": "Ministry of Corporate Affairs (MCA) Dataset",
                "explanation": f"No active or inactive entity under name '{company_name}' was found in the local company master dataset."
            })
            recommendations.append("Company is not cataloged in the local dataset. Perform manual CIN lookup on the official MCA portal.")

        # LinkedIn Component (20 pts max)
        if linkedin_res["verification_status"] == "VERIFIED":
            linkedin_score = 20.0
            evidence.append({
                "category": "Public Presence",
                "signal": "LinkedIn Company Identifier",
                "observed_value": "VERIFIED",
                "reference_value": "Official Company Profile",
                "severity": "LOW",
                "confidence": 0.90,
                "risk_contribution": 0.0,
                "source": "LinkedIn Directory Match",
                "explanation": linkedin_res["verification_message"]
            })
        elif linkedin_res["verification_status"] == "UNVERIFIED":
            linkedin_score = 10.0
        else:
            linkedin_score = 0.0

        # Website Component (15 pts max)
        if website_res["website_verified"]:
            website_score = 15.0
            evidence.append({
                "category": "Digital Presence",
                "signal": "SSL & DNS Resolution",
                "observed_value": "Verified HTTPS",
                "reference_value": "Secure Web Endpoint",
                "severity": "LOW",
                "confidence": 0.95,
                "risk_contribution": 0.0,
                "source": "DNS & SSL Handshake",
                "explanation": f"Domain '{official_domain}' resolved and presented a valid SSL certificate."
            })
        elif official_domain:
            website_score = 5.0
            evidence.append({
                "category": "Digital Presence",
                "signal": "SSL & DNS Resolution",
                "observed_value": "Unreachable / Invalid SSL",
                "reference_value": "Secure Web Endpoint",
                "severity": "HIGH",
                "confidence": 0.90,
                "risk_contribution": 15.0,
                "source": "DNS & SSL Handshake",
                "explanation": website_res["message"]
            })

        # Recruiter Component (10 pts max)
        if recruiter_email:
            if recruiter_res["email_verified"]:
                recruiter_score = 10.0
                evidence.append({
                    "category": "Recruiter Verification",
                    "signal": "Domain Consistency",
                    "observed_value": recruiter_res["recruiter_domain"],
                    "reference_value": official_domain or "",
                    "severity": "LOW",
                    "confidence": 0.95,
                    "risk_contribution": 0.0,
                    "source": "Corporate Email Check",
                    "explanation": recruiter_res["message"]
                })
            else:
                recruiter_score = 0.0
                evidence.append({
                    "category": "Recruiter Verification",
                    "signal": "Domain Consistency",
                    "observed_value": recruiter_res.get("recruiter_domain", "Unknown"),
                    "reference_value": official_domain or "Official Domain",
                    "severity": "HIGH" if recruiter_res.get("typosquatting_detected") else "MEDIUM",
                    "confidence": 0.90,
                    "risk_contribution": 20.0,
                    "source": "Corporate Email Check",
                    "explanation": recruiter_res["message"]
                })
                recommendations.append("Recruiter email does not match official company domain. Verify recruiter identity directly.")
        else:
            recruiter_score = 5.0

        # Calculate Final Trust Score (0 to 100)
        total_trust = mca_score + linkedin_score + website_score + recruiter_score + security_score
        
        # Inactive entities cannot have high trust
        if mca_res["is_inactive"]:
            total_trust = min(total_trust, 25.0)

        total_trust = min(max(total_trust, 0.0), 100.0)

        # Map Trust to Category
        if total_trust >= 90:
            trust_level = "TRUSTED"
        elif total_trust >= 75:
            trust_level = "MOSTLY_TRUSTED"
        elif total_trust >= 60:
            trust_level = "NEEDS_VERIFICATION"
        elif total_trust >= 40:
            trust_level = "SUSPICIOUS"
        else:
            trust_level = "LIKELY_SCAM"

        if not recommendations:
            recommendations.append("Company records and digital presence appear consistent with verified profile.")

        return {
            "company_name": company_name,
            "trust_score": total_trust,
            "risk_level": trust_level,
            "mca_result": mca_res,
            "linkedin_result": linkedin_res,
            "website_result": website_res,
            "recruiter_result": recruiter_res,
            "components": {
                "mca_score": mca_score,
                "linkedin_score": linkedin_score,
                "website_score": website_score,
                "recruiter_score": recruiter_score,
                "security_score": security_score
            },
            "evidence": evidence,
            "recommendations": recommendations
        }
