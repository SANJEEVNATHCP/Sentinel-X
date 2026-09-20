"""
FraudLens AI - Recruiter Email Verification Service
Detects domain mismatches, free mail providers, and typosquatting in recruitment inquiries.
"""

from typing import Dict, Any, Optional
from app.utils.url_utils import extract_domain

FREE_EMAIL_PROVIDERS = {
    "gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "icloud.com",
    "protonmail.com", "aol.com", "mail.com", "zoho.com", "yandex.com"
}

class RecruiterService:
    @staticmethod
    def verify_recruiter_email(recruiter_email: str, company_domain_or_url: Optional[str] = None) -> Dict[str, Any]:
        if not recruiter_email or "@" not in recruiter_email:
            return {
                "email_verified": False,
                "email": recruiter_email or "",
                "domain_match": False,
                "free_email": False,
                "typosquatting_detected": False,
                "risk_score": 30.0,
                "message": "Invalid recruiter email format."
            }

        recruiter_domain = recruiter_email.split("@")[-1].strip().lower()
        is_free_email = recruiter_domain in FREE_EMAIL_PROVIDERS

        official_domain = extract_domain(company_domain_or_url) if company_domain_or_url else ""
        domain_match = False
        typosquatting = False
        risk_score = 0.0
        message = "Official corporate email domain verified."

        if is_free_email:
            risk_score += 40.0
            message = f"Recruiter is communicating from a free public email provider (@{recruiter_domain}) rather than an authenticated corporate domain."
        elif official_domain:
            if recruiter_domain == official_domain or recruiter_domain.endswith(f".{official_domain}"):
                domain_match = True
                risk_score = 0.0
                message = f"Recruiter domain '@{recruiter_domain}' directly matches official company domain '{official_domain}'."
            else:
                # Check for typosquatting / look-alike (e.g. google-careers.com vs google.com)
                base_name = official_domain.split(".")[0]
                if base_name in recruiter_domain:
                    typosquatting = True
                    risk_score += 65.0
                    message = f"Potential typosquatting detected: Recruiter domain '@{recruiter_domain}' contains brand '{base_name}' but differs from official domain '{official_domain}'."
                else:
                    risk_score += 50.0
                    message = f"Recruiter domain '@{recruiter_domain}' does NOT match official company domain '{official_domain}'."
        else:
            message = f"Recruiter domain '@{recruiter_domain}' observed. No company official domain was provided for cross-referencing."

        return {
            "email_verified": domain_match,
            "email": recruiter_email,
            "recruiter_domain": recruiter_domain,
            "official_domain": official_domain,
            "domain_match": domain_match,
            "free_email": is_free_email,
            "typosquatting_detected": typosquatting,
            "risk_score": risk_score,
            "message": message
        }
