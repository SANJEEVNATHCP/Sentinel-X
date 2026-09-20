"""
FraudLens AI - VirusTotal Intelligence Service
Queries the VirusTotal v3 API with timeout guards and graceful UNAVAILABLE fallback.
"""

import base64
import httpx
from typing import Dict, Any
from app.config import settings
from app.logging_config import logger

class VirusTotalService:
    @staticmethod
    async def scan_url(raw_url: str) -> Dict[str, Any]:
        """
        Submits and queries VirusTotal v3 URL intelligence.
        If VIRUSTOTAL_API_KEY is not configured or fails, returns status 'UNAVAILABLE'.
        """
        api_key = settings.VIRUSTOTAL_API_KEY
        if not api_key:
            return {
                "scan_status": "UNAVAILABLE",
                "malicious": 0,
                "suspicious": 0,
                "harmless": 0,
                "undetected": 0,
                "reputation": 0,
                "message": "VirusTotal API key is not configured in backend environment."
            }

        try:
            # VirusTotal v3 URL ID is base64 representation without padding
            url_id = base64.urlsafe_b64encode(raw_url.encode()).decode().strip("=")
            endpoint = f"https://www.virustotal.com/api/v3/urls/{url_id}"
            headers = {
                "x-apikey": api_key,
                "Accept": "application/json"
            }

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(endpoint, headers=headers)
                
                if response.status_code == 200:
                    data = response.json().get("data", {})
                    attributes = data.get("attributes", {})
                    stats = attributes.get("last_analysis_stats", {})
                    reputation = attributes.get("reputation", 0)

                    malicious = stats.get("malicious", 0)
                    suspicious = stats.get("suspicious", 0)
                    harmless = stats.get("harmless", 0)
                    undetected = stats.get("undetected", 0)

                    return {
                        "scan_status": "COMPLETED",
                        "malicious": malicious,
                        "suspicious": suspicious,
                        "harmless": harmless,
                        "undetected": undetected,
                        "reputation": reputation,
                        "message": f"VirusTotal reports {malicious} malicious and {suspicious} suspicious vendor detections."
                    }
                elif response.status_code == 404:
                    # URL not yet analyzed in VT
                    return {
                        "scan_status": "NOT_FOUND",
                        "malicious": 0,
                        "suspicious": 0,
                        "harmless": 0,
                        "undetected": 0,
                        "reputation": 0,
                        "message": "URL has not been previously cataloged by VirusTotal."
                    }
                else:
                    logger.warning(f"VirusTotal API returned status {response.status_code}")
                    return {
                        "scan_status": "UNAVAILABLE",
                        "malicious": 0,
                        "suspicious": 0,
                        "harmless": 0,
                        "undetected": 0,
                        "reputation": 0,
                        "message": f"VirusTotal API returned error status {response.status_code}."
                    }
        except Exception as e:
            logger.warning(f"VirusTotal lookup error: {str(e)}")
            return {
                "scan_status": "UNAVAILABLE",
                "malicious": 0,
                "suspicious": 0,
                "harmless": 0,
                "undetected": 0,
                "reputation": 0,
                "message": "VirusTotal intelligence service is currently unreachable."
            }
