"""
FraudLens AI - Spam URL Dataset Import Script
Imports spam/threat URLs with ACTIVE / INACTIVE status into the database.
"""

import sys
import os
import csv

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine, Base
from app.models.scam_analysis import SpamURL
from app.utils.url_utils import normalize_url, extract_domain

def import_spam_urls(csv_path: str = None) -> None:
    if not csv_path:
        csv_path = os.path.join(os.path.dirname(__file__), "..", "datasets", "spam_urls.csv")

    if not os.path.exists(csv_path):
        print(f"Error: Dataset not found at {csv_path}")
        return

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    imported = 0
    duplicates = 0
    invalid_urls = 0

    try:
        with open(csv_path, mode="r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            for row in reader:
                raw_url = row.get("url", "").strip()
                status = row.get("status", "").strip().upper()

                if not raw_url:
                    continue

                try:
                    norm = normalize_url(raw_url)
                    domain = extract_domain(norm)
                except Exception:
                    invalid_urls += 1
                    continue

                existing = db.query(SpamURL).filter(SpamURL.normalized_url == norm).first()
                if existing:
                    existing.status = status
                    existing.domain = domain
                    duplicates += 1
                else:
                    sp = SpamURL(
                        url=raw_url,
                        normalized_url=norm,
                        domain=domain,
                        status=status,
                        source="FraudLens URL Dataset"
                    )
                    db.add(sp)
                    imported += 1

        db.commit()
        print(f"Spam URL Dataset Import Finished:")
        print(f"  Records Imported: {imported}")
        print(f"  Duplicates Updated: {duplicates}")
        print(f"  Invalid URLs Skipped: {invalid_urls}")
    except Exception as e:
        db.rollback()
        print(f"Error importing spam URLs: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    import_spam_urls()
