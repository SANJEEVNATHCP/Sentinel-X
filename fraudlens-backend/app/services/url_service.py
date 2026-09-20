"""
FraudLens AI - URL Security Analysis Service
Combines URL heuristics, SSRF validation, local dataset lookup, and VirusTotal intelligence.
"""

import re
import urllib.parse
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.utils.url_utils import normalize_url, extract_domain, validate_ssrf_safety
from app.services.spam_dataset_service import SpamDatasetService
from app.services.virustotal_service import VirusTotalService

SUSPICIOUS_KEYWORDS = [
    "login", "verify", "secure", "account", "banking", "update", "kyc",
    "password", "wallet", "support", "refund", "signin", "auth", "claim",
    "free", "gift", "bonus", "winner", "prize", "otp"
]

SUSPICIOUS_TLDS = [
    ".xyz", ".top", ".club", ".live", ".guru", ".vip", ".work", ".cf",
    ".ga", ".ml", ".gq", ".men", ".loan", ".date"
]

class URLService:
    @staticmethod
    def inspect_url_patterns(raw_url: str) -> List[str]:
        """Detects high-risk phishing indicators embedded in URL structure."""
        findings = []
        lowered = raw_url.lower()

        # Check for IP address used as hostname
        parsed = urllib.parse.urlparse(raw_url if "://" in raw_url else f"https://{raw_url}")
        hostname = parsed.hostname or ""
        if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", hostname):
            findings.append("URL hostname is a bare numerical IP address rather than a verified domain name")

        # Check for suspicious top-level domains
        for tld in SUSPICIOUS_TLDS:
            if hostname.endswith(tld):
                findings.append(f"Domain uses high-abuse top-level domain extension '{tld}'")
                break

        # Check for multi-level subdomains (subdomain spoofing)
        parts = hostname.split(".")
        if len(parts) > 3:
            findings.append(f"Excessive sub-domain nesting observed ({len(parts)} levels)")

        # Check for brand imitation and phishing keywords in path or subdomain
        for kw in SUSPICIOUS_KEYWORDS:
            if kw in lowered and not hostname.startswith(kw):
                findings.append(f"Contains security-sensitive keyword '{kw}' commonly observed in credential harvesting")
                break

        # Check for presence of '@' in URL (userinfo spoofing)
        if "@" in raw_url:
            findings.append("URL contains userinfo '@' symbol, a common browser destination spoofing technique")

        # Check if plain HTTP
        if parsed.scheme == "http":
            findings.append("Connection is unencrypted (HTTP) without SSL/TLS transport security")

        return findings

    @classmethod
    async def analyze_url(cls, db: Session, raw_url: str) -> Dict[str, Any]:
        """
        Orchestrates complete URL analysis including SSRF validation,
        local spam dataset status, and VirusTotal threat scanning.
        """
        # 1. SSRF Safety Check & Normalization
        validate_ssrf_safety(raw_url)
        normalized = normalize_url(raw_url)
        domain = extract_domain(normalized)
        is_https = normalized.startswith("https://")

        # 2. Local Threat Dataset Check
        dataset_res = SpamDatasetService.check_url(db, normalized)

        # 3. VirusTotal Scan
        vt_res = await VirusTotalService.scan_url(normalized)

        # 4. Pattern Heuristics
        patterns = cls.inspect_url_patterns(normalized)

        # 5. Evidence & Risk Scoring
        evidence = []
        risk_score = 0.0
        risk_factors = []
        recommendations = []

        # Local Dataset Evidence
        if dataset_res["dataset_found"]:
            status = dataset_res["status"]
            if status == "ACTIVE":
                risk_score += 25.0
                risk_factors.append({"name": "Dataset Match", "weight": 1.0, "contribution": 25.0, "description": "URL is cataloged as ACTIVE in FraudLens Threat Feed"})
                evidence.append({
                    "category": "Domain Threat Feed",
                    "signal": "Local Dataset Status",
                    "observed_value": "ACTIVE",
                    "reference_value": "Threat Feed Catalog",
                    "severity": "HIGH",
                    "confidence": 0.95,
                    "risk_contribution": 25.0,
                    "source": dataset_res["source"],
                    "explanation": "URL appears as an ACTIVE entity in the FraudLens suspicious URL catalog."
                })
            elif status == "INACTIVE":
                risk_score += 35.0
                risk_factors.append({"name": "Inactive Entity Match", "weight": 1.0, "contribution": 35.0, "description": "URL is cataloged as INACTIVE / Defunct in Threat Feed"})
                evidence.append({
                    "category": "Domain Threat Feed",
                    "signal": "Local Dataset Status",
                    "observed_value": "INACTIVE",
                    "reference_value": "Threat Feed Catalog",
                    "severity": "HIGH",
                    "confidence": 0.95,
                    "risk_contribution": 35.0,
                    "source": dataset_res["source"],
                    "explanation": "URL is listed as INACTIVE or defunct in the dataset. Entity may be unauthorized or expired."
                })
        else:
            evidence.append({
                "category": "Domain Threat Feed",
                "signal": "Local Dataset Status",
                "observed_value": "NOT_FOUND",
                "reference_value": "Threat Feed Catalog",
                "severity": "LOW",
                "confidence": 0.90,
                "risk_contribution": 0.0,
                "source": dataset_res["source"],
                "explanation": "URL does not currently appear in the local known threat catalog."
            })

        # VirusTotal Evidence
        if vt_res["scan_status"] == "COMPLETED":
            mal = vt_res["malicious"]
            susp = vt_res["suspicious"]
            if mal > 0:
                vt_points = min(mal * 20.0, 50.0)
                risk_score += vt_points
                risk_factors.append({"name": "Antivirus Engine Flags", "weight": 1.0, "contribution": vt_points, "description": f"{mal} security vendors flagged domain as malicious"})
                evidence.append({
                    "category": "Security Intelligence",
                    "signal": "VirusTotal Vendor Detections",
                    "observed_value": f"{mal} Malicious / {susp} Suspicious",
                    "reference_value": "0 Detections",
                    "severity": "CRITICAL" if mal >= 3 else "HIGH",
                    "confidence": 0.98,
                    "risk_contribution": vt_points,
                    "source": "VirusTotal API v3",
                    "explanation": f"VirusTotal reports {mal} security vendors flagging this target URL as malicious."
                })
            elif susp > 0:
                risk_score += 15.0
                evidence.append({
                    "category": "Security Intelligence",
                    "signal": "VirusTotal Vendor Detections",
                    "observed_value": f"{susp} Suspicious",
                    "reference_value": "0 Detections",
                    "severity": "MEDIUM",
                    "confidence": 0.85,
                    "risk_contribution": 15.0,
                    "source": "VirusTotal API v3",
                    "explanation": f"VirusTotal reports {susp} security vendors flagging this URL as suspicious."
                })
            else:
                evidence.append({
                    "category": "Security Intelligence",
                    "signal": "VirusTotal Vendor Detections",
                    "observed_value": "0 Detections",
                    "reference_value": "0 Detections",
                    "severity": "LOW",
                    "confidence": 0.90,
                    "risk_contribution": 0.0,
                    "source": "VirusTotal API v3",
                    "explanation": "No malicious flags reported across VirusTotal security scanning engines."
                })
        else:
            evidence.append({
                "category": "Security Intelligence",
                "signal": "VirusTotal Status",
                "observed_value": vt_res["scan_status"],
                "reference_value": "Available",
                "severity": "LOW",
                "confidence": 0.50,
                "risk_contribution": 0.0,
                "source": "VirusTotal API v3",
                "explanation": vt_res.get("message", "VirusTotal threat intelligence is unavailable.")
            })

        # Pattern Evidence
        for p in patterns:
            risk_score += 10.0
            evidence.append({
                "category": "URL Structure",
                "signal": "Pattern Anomaly",
                "observed_value": p,
                "reference_value": "Standard Domain Pattern",
                "severity": "MEDIUM",
                "confidence": 0.85,
                "risk_contribution": 10.0,
                "source": "FraudLens Heuristic Engine",
                "explanation": p
            })

        # Score Clamping
        final_score = min(max(risk_score, 0.0), 100.0)
        
        if final_score >= 70:
            level = "HIGH_RISK"
            recommendations.append("Do not enter login credentials, passwords, or personal payment cards on this website.")
            recommendations.append("Close the browser tab immediately and verify through official channels.")
        elif final_score >= 50:
            level = "SUSPICIOUS"
            recommendations.append("Exercise extreme caution. Cross-reference the official website via established search engines.")
        elif final_score >= 25:
            level = "MODERATE"
            recommendations.append("Review SSL certificate and verify that the domain matches the intended organization.")
        else:
            level = "LOW"
            recommendations.append("No immediate threat indicators detected. Continue monitoring standard connection security.")

        return {
            "url": raw_url,
            "normalized_url": normalized,
            "domain": domain,
            "is_https": is_https,
            "local_dataset": dataset_res,
            "virustotal": vt_res,
            "risk_score": final_score,
            "risk_level": level,
            "suspicious_patterns_detected": patterns,
            "evidence": evidence,
            "risk_factors": risk_factors,
            "recommendations": recommendations
        }
