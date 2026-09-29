# FraudLens AI — Production Backend

> **"See the Risk. Understand the Evidence. Act Safely."**

FraudLens AI is an explainable fraud intelligence platform that analyzes suspicious financial transactions, URLs, companies, recruiters, job/offer listings, screenshots, and scam conversations.

Rather than simply outputting an opaque `"SCAM — 87/100"`, FraudLens follows:
```
DETECT  →  VERIFY  →  EXPLAIN  →  RECOMMEND ACTION
```
and produces human-auditable evidence items, observable baseline comparisons, transparent risk contribution weights, and safety recommendations.

---

## 🛡 Key Architectural Principles

1. **Authoritative Company Evaluation**:
   - The backend uses the **Company Master Sample Dataset** (`datasets/companies.csv`) as the primary reference to determine whether a corporate entity is **Active** (real/verified corporate registry) or **Inactive** (high-risk / defunct / unauthorized warning).
   - If marked `Active`: Returns verified registration credentials (CIN, ROC, Registered State, official domain, and official website) with `LOW` risk.
   - If marked `Inactive`: Immediately flags as `HIGH_RISK` (+45 risk penalty), warning that the company is defunct or unauthorized.
   - If not present: Marked as `UNVERIFIED` without inventing company facts.
2. **Dual-Layer ML & Behavioral Profiling**:
   - Supervised `RandomForestClassifier` for fraud scoring.
   - Unsupervised `IsolationForest` for behavioral anomaly detection.
   - Transparent rule engine generating human-readable evidence (e.g. *"Transaction amount ₹48,500 is 26.2x historical average of ₹1,850"*).
3. **Local Spam/Threat Feed Dataset**:
   - Distinct from external scanners. Identifies whether a target URL is cataloged as `ACTIVE` or `INACTIVE` in the local threat dataset, presented alongside VirusTotal vendor flags.
4. **Privacy-First "End Task" Flow**:
   - When an investigation is concluded via `POST /api/investigations/{id}/end`, all raw uploaded documents, spreadsheets, OCR texts, and temporary session caches are **permanently purged** from disk.
   - The derived investigation results (risk score, auditable evidence items, risk factors, recommendations, and executive summaries) remain preserved in the user's Results history.
5. **Zero Changes to Extension**:
   - The companion browser extension directory (`extention/`) is strictly treated as read-only and remains completely untouched.

---

## 📁 Project Structure

```
fraudlens-backend/
├── app/
│   ├── main.py                  # FastAPI entrypoint, middleware, routers
│   ├── config.py                # Pydantic v2 settings
│   ├── database.py              # SQLAlchemy 2.0 engine & SessionLocal
│   ├── dependencies.py          # JWT authentication and user injection
│   ├── logging_config.py        # Structured JSON logging (zero PII leakage)
│   ├── exceptions.py            # Custom domain exceptions
│   ├── security.py              # Bcrypt password hashing & JWT encoding
│   ├── middleware.py            # Tracing headers, security headers, rate limiting
│   ├── schemas/                 # Pydantic v2 validation models
│   ├── models/                  # SQLAlchemy 2.0 ORM models
│   ├── api/                     # FastAPI route handlers
│   ├── services/                # Business logic & verification engines
│   ├── ml/                      # Feature engineering & ML inference
│   ├── mcp/                     # FastMCP investigative server & tools
│   ├── workers/                 # Celery asynchronous task workers
│   └── utils/                   # SSRF defense, URL normalization, temp files
├── datasets/
│   ├── companies.csv            # Company Master Dataset (Active vs Inactive)
│   ├── spam_urls.csv            # Threat feed URLs (ACTIVE vs INACTIVE)
│   └── sample_transactions.csv  # Baseline UPI records
├── models/
│   ├── fraud_model.pkl          # Trained RandomForest classifier
│   ├── anomaly_model.pkl        # Trained IsolationForest detector
│   └── scaler.pkl               # StandardScaler
├── migrations/                  # Alembic database migration scripts
├── scripts/
│   ├── seed_database.py         # Auto-seeder & demo analyst creator
│   ├── import_company_dataset.py# Imports MCA company records
│   ├── import_spam_dataset.py   # Imports spam threat URLs
│   └── train_models.py          # ML model training pipeline
├── tests/                       # Complete Pytest test suite
├── .env.example                 # Environment configuration template
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Production container definition
├── docker-compose.yml           # Multi-service stack (FastAPI, Postgres, Redis, Celery)
└── alembic.ini                  # Alembic migration configuration
```

---

## ⚡ Quickstart (Local Development)

### 1. Prerequisites
- Python 3.11+
- Virtualenv (`python -m venv venv`)

### 2. Install Dependencies
```bash
cd fraudlens-backend
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
# source venv/bin/activate

pip install -r requirements.txt
```

### 3. Configure Environment
```bash
cp .env.example .env
```
*(By default, `.env` uses `sqlite:///./fraudlens.db` for instant local execution without needing PostgreSQL).*

### 4. Train Models & Seed Database
```bash
# 1. Train ML models (RandomForest & IsolationForest)
python scripts/train_models.py

# 2. Seed database with Company Master dataset and Spam URLs
python scripts/seed_database.py
```
*Creates default demo account:*
- **Email:** `demo@fraudlens.ai`
- **Password:** `FraudLens@2026`

### 5. Start the FastAPI Server
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
- Interactive Swagger API Documentation: [http://localhost:8000/docs](http://localhost:8000/docs)
- Alternative ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- Health Check: [http://localhost:8000/api/health](http://localhost:8000/api/health)

---

## 🐳 Docker Deployment

To launch the full production stack including PostgreSQL, Redis, Celery worker, and FastAPI:

```bash
docker compose up --build
```

Services:
- **FastAPI Backend:** `http://localhost:8000`
- **PostgreSQL 16:** `localhost:5432` (`fraudlens_db`)
- **Redis 7:** `localhost:6379`
- **Celery Worker:** Running in container processing background tasks

---

## 🧪 Running Automated Tests

Run the full test suite using `pytest`:

```bash
pytest tests/ -v
```

Covered test suites:
- `test_auth.py`: Registration, duplicate email rejection, login, JWT verification.
- `test_company.py`: Active vs. Inactive company dataset verification and recruiter email consistency.
- `test_spam_dataset.py`: Local threat dataset `ACTIVE`, `INACTIVE`, and `NOT_FOUND` queries.
- `test_url_analysis.py`: SSRF security defense blocking loopback, RFC 1918 private IPs, and cloud metadata.
- `test_linkedin.py`: LinkedIn company URL verification and sub-path rejection.
- `test_transactions.py`: UPI statement parsing, behavioral baselining, and ML anomaly detection.
- `test_privacy.py`: End-Task execution ensuring raw files are permanently purged while derived results remain intact.
- `test_results.py`: Report downloads (PDF and JSON) and history management.

---

## 📡 Core API Endpoints

| Category | Method | Endpoint | Description |
| :--- | :--- | :--- | :--- |
| **Auth** | `POST` | `/api/auth/register` | Register new user account |
| | `POST` | `/api/auth/login` | Login and obtain signed JWT access token |
| | `POST` | `/api/auth/logout` | Invalidate/logout user session |
| | `GET` | `/api/auth/me` | Fetch authenticated user profile |
| **Dashboard** | `GET` | `/api/dashboard` | Real user metrics (zero fabrication) |
| **Transactions** | `POST` | `/api/transactions/analyze` | Ingest UPI CSV/XLSX & run ML profiling |
| | `GET` | `/api/transactions/{id}` | Query transaction investigation details |
| **Scam & URLs** | `POST` | `/api/scam/analyze` | Multi-signal scan (URL, company, text) |
| | `POST` | `/api/scam/url` | SSRF-safe URL threat scan & dataset check |
| | `POST` | `/api/scam/image-analysis` | Screenshot & phishing chat classifier |
| **Company** | `POST` | `/api/company/verify` | Check MCA Company Master dataset (Active/Inactive) |
| | `POST` | `/api/company/linkedin` | Check permitted LinkedIn presence |
| | `POST` | `/api/company/offer-letter` | Upload offer letter PDF/image for verification |
| | `POST` | `/api/company/trust-score` | Compute 0-100 composite corporate trust score |
| **Investigation** | `GET` | `/api/investigations` | List user investigations |
| | `GET` | `/api/investigations/{id}` | Real-time status & stage progress |
| | `POST` | `/api/investigations/{id}/what-if`| Recalculate score toggling individual risk factors |
| | `POST` | `/api/investigations/{id}/end` | **End Task:** Purge raw files, keep derived results |
| **Results** | `GET` | `/api/results` | Query persistent results history |
| | `GET` | `/api/results/{id}` | Full evidence, risk factors, and recommendations |
| | `GET` | `/api/results/{id}/download` | Download official PDF or JSON report |
| | `DELETE`| `/api/results/{id}` | Explicitly delete result from history |
| **Privacy** | `GET` | `/api/privacy` | Data minimization & retention policies |
| | `POST` | `/api/privacy/delete-session`| Immediate session cleanup |
| **System** | `GET` | `/api/health` | Comprehensive subsystem health check |
