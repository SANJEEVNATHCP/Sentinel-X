"""
FraudLens AI - FastMCP Investigation Server
Exposes structured investigative tools for AI agents and LLM orchestration.
"""

from typing import Dict, Any, Optional
from app.services.mca_service import MCAService
from app.services.linkedin_service import LinkedInService
from app.services.website_service import WebsiteService
from app.services.recruiter_service import RecruiterService
from app.services.url_service import URLService
from app.services.spam_dataset_service import SpamDatasetService
from app.services.virustotal_service import VirusTotalService
from app.services.company_service import CompanyService
from app.database import SessionLocal

class FraudLensMCPServer:
    """FastMCP Compatible Tool Provider for AI Investigators."""

    @staticmethod
    def verify_company_mca(company_name: str, domain: Optional[str] = None) -> Dict[str, Any]:
        """Queries authoritative MCA Company Master dataset for Active vs Inactive status."""
        db = SessionLocal()
        try:
            return MCAService.verify_company(db, company_name, domain)
        finally:
            db.close()

    @staticmethod
    def verify_company_presence(linkedin_url: str) -> Dict[str, Any]:
        """Validates company LinkedIn presence using permitted public URL checks."""
        return LinkedInService.verify_company_presence(linkedin_url)

    @staticmethod
    def verify_company_website(domain_or_url: str) -> Dict[str, Any]:
        """Checks DNS reachability and SSL security without SSRF exposure."""
        return WebsiteService.verify_website(domain_or_url)

    @staticmethod
    def verify_recruiter(recruiter_email: str, official_domain: Optional[str] = None) -> Dict[str, Any]:
        """Detects domain mismatches, free mail addresses, and typosquatting."""
        return RecruiterService.verify_recruiter_email(recruiter_email, official_domain)

    @staticmethod
    def get_spam_dataset_status(url: str) -> Dict[str, Any]:
        """Returns exact status in FraudLens threat feed: ACTIVE, INACTIVE, or NOT_FOUND."""
        db = SessionLocal()
        try:
            return SpamDatasetService.check_url(db, url)
        finally:
            db.close()

    @staticmethod
    async def get_virustotal_result(url: str) -> Dict[str, Any]:
        """Queries VirusTotal vendor detection stats."""
        return await VirusTotalService.scan_url(url)

    @staticmethod
    def get_trust_score(company_name: str, domain: Optional[str] = None, recruiter_email: Optional[str] = None) -> Dict[str, Any]:
        """Calculates 0-100 composite trust score across all corporate indicators."""
        db = SessionLocal()
        try:
            return CompanyService.evaluate_company(db, company_name, domain=domain, recruiter_email=recruiter_email)
        finally:
            db.close()

mcp_server = FraudLensMCPServer()
