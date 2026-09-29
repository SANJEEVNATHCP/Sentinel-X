"""
FraudLens AI - Pytest Fixtures & Test Setup
Uses an isolated in-memory SQLite database with StaticPool and FastAPI TestClient.
"""

import os
import sys
import csv
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import Base, get_db
from app.main import app
from app.models.user import User
from app.models.company_check import Company
from app.models.scam_analysis import SpamURL
from app.security import get_password_hash, create_access_token
from app.utils.normalization import normalize_company_name
from app.utils.url_utils import normalize_url, extract_domain

TEST_DB_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    # 1. Create test user
    u = User(
        id="usr_test_123",
        full_name="Test Security Analyst",
        email="test_analyst@fraudlens.ai",
        password_hash=get_password_hash("TestPassword@123"),
        is_active=True
    )
    db.add(u)

    # 2. Seed Companies dataset
    csv_comp = os.path.join(os.path.dirname(__file__), "..", "datasets", "companies.csv")
    if os.path.exists(csv_comp):
        with open(csv_comp, mode="r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            for r in reader:
                cin = r.get("cin", "").strip()
                name = r.get("company_name", "").strip()
                if cin and name:
                    comp = Company(
                        cin=cin,
                        company_name=name,
                        normalized_name=normalize_company_name(name),
                        company_status=r.get("company_status", "").strip(),
                        brand_name=r.get("brand_name", "").strip(),
                        official_domain=r.get("official_domain", "").strip().lower(),
                        official_website=r.get("official_website", "").strip(),
                        registered_state=r.get("registered_state", "").strip(),
                        registrar_of_companies=r.get("registrar_of_companies", "").strip(),
                        verification_note=r.get("verification_note", "").strip()
                    )
                    db.add(comp)

    # 3. Seed Spam URLs
    csv_spam = os.path.join(os.path.dirname(__file__), "..", "datasets", "spam_urls.csv")
    if os.path.exists(csv_spam):
        with open(csv_spam, mode="r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            for r in reader:
                u_raw = r.get("url", "").strip()
                st = r.get("status", "").strip().upper()
                if u_raw:
                    try:
                        n_url = normalize_url(u_raw)
                        dom = extract_domain(n_url)
                        sp = SpamURL(
                            url=u_raw,
                            normalized_url=n_url,
                            domain=dom,
                            status=st,
                            source="FraudLens URL Dataset"
                        )
                        db.add(sp)
                    except Exception:
                        pass

    db.commit()
    db.close()

    yield

    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture
def auth_headers():
    token = create_access_token({"sub": "usr_test_123", "email": "test_analyst@fraudlens.ai"})
    return {"Authorization": f"Bearer {token}"}
