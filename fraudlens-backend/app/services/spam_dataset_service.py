"""
FraudLens AI - Local Spam/Threat URL Dataset Service
Searches indexed dataset and returns ACTIVE, INACTIVE, or NOT_FOUND status.
"""

import os
import csv
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from app.models.scam_analysis import SpamURL
from app.utils.url_utils import normalize_url, extract_domain
from app.config import settings

class SpamDatasetService:
    _csv_cache: Optional[List[Dict[str, Any]]] = None

    @classmethod
    def _load_csv_cache(cls) -> List[Dict[str, Any]]:
        if cls._csv_cache is not None:
            return cls._csv_cache

        csv_path = os.path.join(settings.DATASETS_DIR, "spam_urls.csv")
        records = []
        if os.path.exists(csv_path):
            with open(csv_path, mode="r", encoding="utf-8", errors="ignore") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    u = row.get("url", "").strip()
                    s = row.get("status", "").strip().upper()
                    if u and s:
                        records.append({
                            "url": u,
                            "domain": extract_domain(u),
                            "status": s
                        })
        cls._csv_cache = records
        return records

    @classmethod
    def check_url(cls, db: Optional[Session], raw_url: str) -> Dict[str, Any]:
        """
        Queries the local dataset for the specified URL or domain.
        Returns exact dataset status: ACTIVE, INACTIVE, or NOT_FOUND.
        """
        try:
            norm_url = normalize_url(raw_url)
            domain = extract_domain(raw_url)
        except Exception:
            return {
                "dataset_found": False,
                "status": "NOT_FOUND",
                "source": "FraudLens URL Dataset",
                "domain": ""
            }

        match = None

        # 1. Query Database first
        if db:
            match = db.query(SpamURL).filter(
                (SpamURL.normalized_url == norm_url) |
                (SpamURL.domain == domain)
            ).first()

        # 2. Fallback to cached CSV
        if not match:
            rows = cls._load_csv_cache()
            for r in rows:
                if r["domain"] == domain or r["url"].rstrip("/") == norm_url.rstrip("/"):
                    return {
                        "dataset_found": True,
                        "status": r["status"],
                        "source": "FraudLens URL Dataset",
                        "domain": domain
                    }

        if match:
            return {
                "dataset_found": True,
                "status": match.status.upper(),
                "source": match.source or "FraudLens URL Dataset",
                "domain": domain
            }

        return {
            "dataset_found": False,
            "status": "NOT_FOUND",
            "source": "FraudLens URL Dataset",
            "domain": domain
        }

    @classmethod
    def lookup_url(cls, db: Optional[Session], raw_url: str) -> Dict[str, Any]:
        """Alias for check_url providing backwards compatibility with both 'found' and 'dataset_found'."""
        res = cls.check_url(db, raw_url)
        res["found"] = res.get("dataset_found", False)
        return res

