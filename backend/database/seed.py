import sys
from datetime import datetime, timezone
from pathlib import Path

# Ensure root directory is on python path when run directly
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.database.database import SessionLocal, init_db
from backend.database.models import Alert, Investigation, Transaction, User


def seed_database():
    """Seeds the SQLite database with initial prototype data."""
    init_db()
    db = SessionLocal()

    try:
        # Check if already seeded
        existing_txn = db.query(Transaction).filter_by(transaction_id="TXN5721").first()
        if existing_txn:
            print("[INFO] Database already contains primary demo transaction TXN5721. Skipping duplicate seed.")
            return

        print("[INFO] Seeding database with demo data...")

        # 1. Demo User: Regular profile
        demo_user = User(
            user_id="USR1001",
            avg_transaction_amount=1250.0,
            normal_transaction_frequency=3.0,
            normal_location="Mumbai, IN",
        )
        db.merge(demo_user)

        # 2. Baseline Normal Transaction (for comparison)
        normal_txn = Transaction(
            transaction_id="TXN5720",
            user_id="USR1001",
            amount=850.0,
            timestamp=datetime(2026, 9, 18, 14, 20, 0, tzinfo=timezone.utc),
            device_id="DEV_PHONE_PRIMARY_441",
            beneficiary_id="BENEF_ELECTRICITY_BOARD",
            location="Mumbai, IN",
            is_new_device=False,
            is_new_beneficiary=False,
        )
        db.merge(normal_txn)

        # 3. Suspicious Primary Demo Transaction: TXN5721
        # Flags: amount=24999 (well above 1250 avg), new device=True, new beneficiary=True,
        # unusual time=02:45 AM, unusual location="Lagos, NG" (vs normal "Mumbai, IN")
        suspicious_txn = Transaction(
            transaction_id="TXN5721",
            user_id="USR1001",
            amount=24999.0,
            timestamp=datetime(2026, 9, 19, 2, 45, 0, tzinfo=timezone.utc),
            device_id="DEV_UNRECOGNIZED_NODE_99",
            beneficiary_id="BENEF_UNVERIFIED_CRYPTO_771",
            location="Lagos, NG",
            is_new_device=True,
            is_new_beneficiary=True,
        )
        db.merge(suspicious_txn)

        # 4. Prototype Alert record for TXN5721
        demo_alert = Alert(
            transaction_id="TXN5721",
            risk_score=94.5,
            risk_level="HIGH",
            status="PENDING",
            created_at=datetime(2026, 9, 19, 2, 45, 12, tzinfo=timezone.utc),
        )
        db.add(demo_alert)

        # 5. Prototype Investigation question for TXN5721
        demo_investigation = Investigation(
            transaction_id="TXN5721",
            question="Security Alert: Did you authorize a transaction of INR 24,999 to BENEF_UNVERIFIED_CRYPTO_771 at 02:45 AM from an unknown device in Lagos, NG?",
            response=None,
            created_at=datetime(2026, 9, 19, 2, 45, 30, tzinfo=timezone.utc),
        )
        db.add(demo_investigation)

        db.commit()
        print("[SUCCESS] Successfully seeded database with primary demo transaction TXN5721 and related records.")
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Failed to seed database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
