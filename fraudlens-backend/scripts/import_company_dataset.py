"""
FraudLens AI - Company Dataset Import Script
Imports company master records from datasets/companies.csv into the database.
"""

import sys
import os
import csv

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine, Base
from app.models.company_check import Company
from app.utils.normalization import normalize_company_name

def import_companies(csv_path: str = None) -> None:
    if not csv_path:
        csv_path = os.path.join(os.path.dirname(__file__), "..", "datasets", "companies.csv")

    if not os.path.exists(csv_path):
        print(f"Error: Dataset not found at {csv_path}")
        return

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    imported = 0
    updated = 0

    try:
        with open(csv_path, mode="r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            for row in reader:
                cin = row.get("cin", "").strip()
                name = row.get("company_name", "").strip()
                status = row.get("company_status", "").strip()

                if not cin or not name:
                    continue

                norm_name = normalize_company_name(name)
                existing = db.query(Company).filter(Company.cin == cin).first()

                if existing:
                    existing.company_name = name
                    existing.normalized_name = norm_name
                    existing.company_status = status
                    existing.brand_name = row.get("brand_name", "").strip()
                    existing.official_domain = row.get("official_domain", "").strip().lower()
                    existing.official_website = row.get("official_website", "").strip()
                    existing.registered_state = row.get("registered_state", "").strip()
                    existing.registrar_of_companies = row.get("registrar_of_companies", "").strip()
                    existing.verification_note = row.get("verification_note", "").strip()
                    updated += 1
                else:
                    c = Company(
                        cin=cin,
                        company_name=name,
                        normalized_name=norm_name,
                        company_status=status,
                        company_class=row.get("company_class", "").strip(),
                        company_category=row.get("company_category", "").strip(),
                        registered_state=row.get("registered_state", "").strip(),
                        registrar_of_companies=row.get("registrar_of_companies", "").strip(),
                        date_of_registration=row.get("date_of_registration", "").strip(),
                        brand_name=row.get("brand_name", "").strip(),
                        official_domain=row.get("official_domain", "").strip().lower(),
                        official_website=row.get("official_website", "").strip(),
                        domain_status=row.get("domain_status", "").strip(),
                        domain_match_type=row.get("domain_match_type", "").strip(),
                        primary_authority=row.get("primary_authority", "").strip(),
                        reference_dataset=row.get("reference_dataset", "").strip(),
                        verification_note=row.get("verification_note", "").strip()
                    )
                    db.add(c)
                    imported += 1

        db.commit()
        print(f"Company Dataset Import Finished: {imported} imported, {updated} updated.")
    except Exception as e:
        db.rollback()
        print(f"Error during import: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    import_companies()
