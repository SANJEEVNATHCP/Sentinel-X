"""ScamShield URL Analysis Service for FraudSentinel X.

Integrates with external threat intelligence APIs (VirusTotal, Google Safe Browsing)
or local prototype heuristics when external providers are not configured.

API credentials are read strictly from environment variables and never exposed.
"""

import os
import re
from typing import Any, Dict, List
from urllib.parse import urlparse


def analyze_url(url: str) -> Dict[str, Any]:
    """Analyzes a URL for scam, phishing, or malicious indicators.

    Returns structured analysis containing url, risk_score, risk_level,
    indicators, provider, and verification status.
    """
    cleaned_url = url.strip()
    if not cleaned_url.startswith(("http://", "https://")):
        cleaned_url = "https://" + cleaned_url

    parsed = urlparse(cleaned_url)
    hostname = (parsed.hostname or "").lower()
    path = parsed.path.lower()

    # 1. Check for external threat intelligence API configuration
    vt_api_key = os.getenv("VIRUSTOTAL_API_KEY")
    gsb_api_key = os.getenv("GOOGLE_SAFE_BROWSING_API_KEY")

    if vt_api_key:
        return _query_virustotal(cleaned_url, vt_api_key)
    elif gsb_api_key:
        return _query_safe_browsing(cleaned_url, gsb_api_key)

    # 2. Local Prototype Analysis when external provider is unavailable
    # Note: We do NOT invent threat-intelligence results. We analyze visible URL patterns
    # and clearly mark external verification as unavailable.
    indicators: List[str] = []
    risk_score = 0.0

    # Pattern heuristics
    ip_pattern = r"^(\d{1,3}\.){3}\d{1,3}$"
    if re.match(ip_pattern, hostname):
        indicators.append("Direct IP address used instead of domain name")
        risk_score += 45.0

    suspicious_keywords = ["job", "recruitment", "crypto", "free", "login", "verify", "secure", "bank", "upi"]
    matched_keywords = [kw for kw in suspicious_keywords if kw in path or kw in hostname]
    if matched_keywords:
        indicators.append(f"Contains high-risk target keywords: {', '.join(matched_keywords)}")
        risk_score += 25.0

    suspicious_tlds = [".xyz", ".top", ".buzz", ".work", ".click", ".fit"]
    if any(hostname.endswith(tld) for tld in suspicious_tlds):
        indicators.append("Uncommon / high-abuse top-level domain")
        risk_score += 20.0

    if len(hostname.split(".")) > 3:
        indicators.append("Excessive subdomain nesting")
        risk_score += 15.0

    risk_score = min(risk_score, 100.0)
    if risk_score >= 70:
        risk_level = "High"
    elif risk_score >= 35:
        risk_level = "Medium"
    elif risk_score > 0:
        risk_level = "Low"
    else:
        risk_level = "Clean"

    return {
        "url": url,
        "risk_score": float(risk_score),
        "risk_level": risk_level,
        "indicators": indicators,
        "status": "External verification unavailable (API key not configured)",
        "provider": "Prototype Heuristic Analyzer",
    }


def _query_virustotal(url: str, api_key: str) -> Dict[str, Any]:
    """Queries VirusTotal API v3 for URL reputation without exposing credentials."""
    import base64
    import json
    import urllib.error
    import urllib.request

    url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")
    req_url = f"https://www.virustotal.com/api/v3/urls/{url_id}"

    req = urllib.request.Request(
        req_url,
        headers={
            "x-apikey": api_key,
            "Accept": "application/json",
            "User-Agent": "FraudSentinel-X/0.1.0",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            stats = data.get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
            malicious = stats.get("malicious", 0)
            suspicious = stats.get("suspicious", 0)

            total_flags = malicious + suspicious
            risk_score = min(total_flags * 15.0, 100.0)
            risk_level = "High" if total_flags >= 3 else ("Medium" if total_flags >= 1 else "Low")

            indicators = []
            if malicious > 0:
                indicators.append(f"{malicious} security vendor(s) flagged this URL as malicious")
            if suspicious > 0:
                indicators.append(f"{suspicious} vendor(s) flagged this URL as suspicious")

            return {
                "url": url,
                "risk_score": float(risk_score),
                "risk_level": risk_level,
                "indicators": indicators,
                "status": "External verification completed",
                "provider": "VirusTotal v3",
            }
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return {
                "url": url,
                "risk_score": 0.0,
                "risk_level": "Clean",
                "indicators": ["URL not previously submitted to VirusTotal"],
                "status": "External verification completed (clean/unseen)",
                "provider": "VirusTotal v3",
            }
        return {
            "url": url,
            "risk_score": 0.0,
            "risk_level": "Unknown",
            "indicators": [],
            "status": "External verification unavailable",
            "provider": "VirusTotal v3",
        }
    except Exception:
        return {
            "url": url,
            "risk_score": 0.0,
            "risk_level": "Unknown",
            "indicators": [],
            "status": "External verification unavailable",
            "provider": "VirusTotal v3",
        }


def _query_safe_browsing(url: str, api_key: str) -> Dict[str, Any]:
    """Stub for Google Safe Browsing if configured."""
    return {
        "url": url,
        "risk_score": 0.0,
        "risk_level": "Unknown",
        "indicators": [],
        "status": "External verification unavailable",
        "provider": "Google Safe Browsing",
    }
