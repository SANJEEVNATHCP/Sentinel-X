"""
FraudLens AI - Company Website Verification Service
Checks DNS resolution, HTTPS, reachability, and SSRF security without unsafe requests.
"""

import socket
import ssl
from typing import Dict, Any
from app.utils.url_utils import extract_domain, validate_ssrf_safety

class WebsiteService:
    @staticmethod
    def verify_website(target_url_or_domain: str) -> Dict[str, Any]:
        """
        Performs safe DNS and SSL certificate handshake checks.
        Rejects SSRF attempts to private networks.
        """
        domain = extract_domain(target_url_or_domain)
        if not domain:
            return {
                "website_verified": False,
                "ssl_valid": False,
                "domain_exists": False,
                "domain": "",
                "message": "Invalid or missing domain."
            }

        # SSRF Protection
        try:
            validate_ssrf_safety(domain)
        except Exception as e:
            return {
                "website_verified": False,
                "ssl_valid": False,
                "domain_exists": False,
                "domain": domain,
                "message": f"Security restriction: {str(e)}"
            }

        domain_exists = False
        ssl_valid = False

        # DNS Check
        try:
            addr_info = socket.getaddrinfo(domain, 443, socket.AF_INET, socket.SOCK_STREAM)
            if addr_info:
                domain_exists = True
        except Exception:
            domain_exists = False

        # SSL Check
        if domain_exists:
            try:
                context = ssl.create_default_context()
                with socket.create_connection((domain, 443), timeout=3.0) as sock:
                    with context.wrap_socket(sock, server_hostname=domain) as ssock:
                        cert = ssock.getpeercert()
                        if cert:
                            ssl_valid = True
            except Exception:
                ssl_valid = False

        return {
            "website_verified": domain_exists and ssl_valid,
            "ssl_valid": ssl_valid,
            "domain_exists": domain_exists,
            "domain": domain,
            "message": "Website domain resolved and valid SSL/TLS certificate confirmed." if (domain_exists and ssl_valid) else "Domain could not establish verified SSL/TLS secure connection."
        }
