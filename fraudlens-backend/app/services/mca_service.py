"""
FraudLens AI - MCA & Company Master Dataset Evaluation Service
Uses the authoritative Company Master Dataset as the primary reference to verify
whether a company is Active (real) or Inactive (fake/defunct).
"""

import os
import csv
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from app.models.company_check import Company
from app.utils.normalization import normalize_company_name
from app.utils.url_utils import extract_domain
from app.config import settings

class MCAService:
    _csv_cache: Optional[List[Dict[str, Any]]] = None

    @classmethod
    def _load_csv_fallback(cls) -> List[Dict[str, Any]]:
        if cls._csv_cache is not None:
            return cls._csv_cache

        csv_path = os.path.join(settings.DATASETS_DIR, "companies.csv")
        records = []
        if os.path.exists(csv_path):
            with open(csv_path, mode="r", encoding="utf-8", errors="ignore") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    records.append(row)
        cls._csv_cache = records
        return records

    @classmethod
    def verify_company(cls, db: Optional[Session], company_name: str, domain: Optional[str] = None) -> Dict[str, Any]:
        """
        Evaluates a company using the authoritative MCA Company Master Dataset.
        Identifies whether the company is Active (real) or Inactive (fake/defunct).
        """
        normalized_query = normalize_company_name(company_name)
        extracted_query_domain = extract_domain(domain) if domain else ""

        match = None

        # 1. Check Database first if session provided
        if db:
            query = db.query(Company)
            # Try exact CIN match
            match = query.filter(Company.cin.ilike(company_name.strip())).first()
            
            # Try normalized name or brand name match
            if not match and normalized_query:
                match = query.filter(
                    (Company.normalized_name == normalized_query) |
                    (Company.brand_name.ilike(normalized_query)) |
                    (Company.company_name.ilike(f"%{normalized_query}%"))
                ).first()

            # Try official domain match
            if not match and extracted_query_domain:
                match = query.filter(Company.official_domain == extracted_query_domain).first()

        # 2. Fallback to reading CSV if database is empty or not seeded
        if not match:
            rows = cls._load_csv_fallback()
            for r in rows:
                cin = r.get("cin", "").strip()
                name = r.get("company_name", "").strip()
                norm_name = normalize_company_name(name)
                brand = r.get("brand_name", "").strip()
                norm_brand = normalize_company_name(brand)
                off_domain = r.get("official_domain", "").strip().lower()

                if cin.lower() == company_name.strip().lower():
                    match = r
                    break
                if normalized_query and (normalized_query == norm_name or normalized_query == norm_brand or normalized_query in norm_name):
                    match = r
                    break
                if extracted_query_domain and off_domain == extracted_query_domain:
                    match = r
                    break

        if match:
            # Handle object vs dictionary
            if isinstance(match, Company):
                cin = match.cin
                name = match.company_name
                status = match.company_status
                brand = match.brand_name
                off_domain = match.official_domain
                off_website = match.official_website
                roc = match.registrar_of_companies
                state = match.registered_state
                note = match.verification_note
            else:
                cin = match.get("cin")
                name = match.get("company_name")
                status = match.get("company_status")
                brand = match.get("brand_name")
                off_domain = match.get("official_domain")
                off_website = match.get("official_website")
                roc = match.get("registrar_of_companies")
                state = match.get("registered_state")
                note = match.get("verification_note")

            is_active = (status.lower() == "active")
            is_inactive = (status.lower() == "inactive")

            # Check domain consistency if domain was provided
            domain_match = None
            if extracted_query_domain and off_domain:
                domain_match = (extracted_query_domain == off_domain.lower())

            return {
                "mca_verified": True,
                "company_status": status,
                "is_active": is_active,
                "is_inactive": is_inactive,
                "cin": cin,
                "company_name": name,
                "brand_name": brand,
                "official_domain": off_domain,
                "official_website": off_website,
                "registered_state": state,
                "roc": roc,
                "domain_match": domain_match,
                "verification_source": "MCA Company Master Dataset",
                "verification_note": note or ("Active corporate record verified." if is_active else "Company marked as INACTIVE."),
                "risk_level": "HIGH_RISK" if is_inactive else "LOW"
            }

        # Not found in authoritative dataset
        return {
            "mca_verified": False,
            "company_status": "NOT_FOUND",
            "is_active": False,
            "is_inactive": False,
            "cin": None,
            "company_name": company_name,
            "brand_name": None,
            "official_domain": None,
            "official_website": None,
            "registered_state": None,
            "roc": None,
            "domain_match": None,
            "verification_source": "MCA Company Master Dataset",
            "verification_note": f"No entity matching '{company_name}' was found in the authoritative company master dataset.",
            "risk_level": "UNVERIFIED"
        }
