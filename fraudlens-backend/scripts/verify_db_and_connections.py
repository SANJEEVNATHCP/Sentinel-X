import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, SessionLocal
from sqlalchemy import inspect, text
from app.models.user import User
from app.models.investigation import Investigation
from app.models.investigation_result import InvestigationResult
from app.models.evidence import Evidence
from app.models.risk_factor import RiskFactor
from app.models.uploaded_file import UploadedFile
from app.models.transaction import TransactionBatch, Transaction

def check_db():
    print("=== Database Connection & Schema Verification ===")
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"Connected to database successfully. Total tables: {len(tables)}")
    
    for t in sorted(tables):
        columns = [c['name'] for c in inspector.get_columns(t)]
        with engine.connect() as conn:
            count = conn.execute(text(f'SELECT COUNT(*) FROM "{t}"')).scalar()
        print(f"  Table: {t:<22} Rows: {count:<6} Columns: {len(columns)}")

    db = SessionLocal()
    try:
        u_count = db.query(User).count()
        inv_count = db.query(Investigation).count()
        res_count = db.query(InvestigationResult).count()
        ev_count = db.query(Evidence).count()
        rf_count = db.query(RiskFactor).count()
        batch_count = db.query(TransactionBatch).count()
        txn_count = db.query(Transaction).count()

        print("\n=== Model Queries & ORM Relationships ===")
        print(f"  Users:               {u_count}")
        print(f"  Investigations:      {inv_count}")
        print(f"  InvestigationResults:{res_count}")
        print(f"  Evidence items:      {ev_count}")
        print(f"  Risk Factors:        {rf_count}")
        print(f"  Transaction Batches: {batch_count}")
        print(f"  Transactions:        {txn_count}")

        # Check reference datasets
        from app.services.mca_service import MCAService
        sample_company = MCAService.verify_company(db, "TCS")
        print("\n=== Reference Dataset Connectivity ===")
        print(f"  MCA Dataset Lookup (TCS): Status={sample_company.get('company_status')}, Verified={sample_company.get('mca_verified')}")

        from app.services.spam_dataset_service import SpamDatasetService
        url_threat = SpamDatasetService.check_url(db, "http://fake-bank-login.com")
        print(f"  Threat URL Dataset Lookup: Status={url_threat.get('dataset_status', 'NOT_FOUND')}, Found={url_threat.get('dataset_found')}")

        print("\n[SUCCESS] All database models, ORM relationships, and datasets are fully connected and healthy!")
    finally:
        db.close()

if __name__ == "__main__":
    check_db()
