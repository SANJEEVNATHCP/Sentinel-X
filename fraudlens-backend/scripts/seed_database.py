"""
FraudLens AI - Database Seeder
Seeds reference datasets and creates default demo user.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models.user import User
from app.security import get_password_hash
from scripts.import_company_dataset import import_companies
from scripts.import_spam_dataset import import_spam_urls

def seed_default_user(db: Session):
    existing = db.query(User).filter(User.email == "demo@fraudlens.ai").first()
    if not existing:
        demo = User(
            full_name="FraudLens Demo Analyst",
            email="demo@fraudlens.ai",
            password_hash=get_password_hash("FraudLens@2026"),
            is_active=True
        )
        db.add(demo)
        db.commit()
        print("Demo User created: demo@fraudlens.ai (Password: FraudLens@2026)")

def auto_seed_if_empty(db: Session):
    from app.models.company_check import Company
    if db.query(Company).count() == 0:
        import_companies()
        import_spam_urls()
        seed_default_user(db)

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        import_companies()
        import_spam_urls()
        seed_default_user(db)
        print("Database seed complete.")
    finally:
        db.close()
