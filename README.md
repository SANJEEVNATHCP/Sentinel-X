# 🛡️ Sentinel X

> **AI-Powered Fraud Detection, Scam Intelligence & Investigation Platform**

**Tagline:** *Detect → Explain → Connect → Verify → Investigate*

FraudSentinel X is an AI-powered cybersecurity platform built for a 24-hour AI Hackathon. It detects suspicious UPI transactions, phishing websites, fake companies, fake recruiters, and job scams using Machine Learning, Explainable AI, Threat Intelligence APIs, and an AI Investigation Assistant powered by MCP (Model Context Protocol).

---

## 🚀 Problem Statement

Build an AI system that detects fraud or anomalies in domains such as UPI transactions, fake job postings, phishing websites, scam listings, and digital fraud, while providing a confidence score and a clear explanation.

**FraudSentinel X solves this by combining:**

- 🤖 AI/ML Fraud Detection
- 🔍 Scam Intelligence
- 📊 Explainable AI
- 🌐 Threat Intelligence APIs
- 🕸️ Relationship Graph Analysis
- 🧠 AI Investigation Assistant (Gemini + MCP)
- 🔒 Privacy-by-Design Architecture

---

# ✨ Key Features

## 💳 AI Fraud Detection

- Detect suspicious UPI transactions.
- Risk Score (0–100).
- Isolation Forest for anomaly detection.
- XGBoost classifier for fraud prediction.
- Behavioural anomaly detection.

## 📊 Explainable AI

- SHAP-based feature explanations.
- Shows exactly why a transaction is suspicious.
- Top contributing fraud indicators.

## 🕸️ Relationship Graph

Visual graph connecting:

- Users
- Devices
- Beneficiaries
- Transactions
- QR Merchants
- Suspicious entities

Built using **NetworkX**.

## 🛡️ ScamShield

Detects:

- Phishing URLs
- Malware URLs
- Fake Job Posts
- Fake Recruiters
- Fake Company Websites

Provides a **Composite Scam Risk Score**.

## 🌐 URL Threat Intelligence

Checks URLs using external security APIs.

Supported providers:

- VirusTotal
- Google Safe Browsing
- URLScan
- AbuseIPDB

## 🏢 Company Verification

Verify whether an Indian company exists using **Ministry of Corporate Affairs (MCA)** information.

Checks:

- Registration status
- CIN / LLPIN
- Incorporation date
- Active / Strike-off status

## 👔 Recruiter Verification

- Email domain verification.
- Company domain matching.
- Public recruiter/company consistency checks.
- Job posting analysis.

## 🤖 AI Investigator (Gemini + MCP)

Ask questions like:

- Why is TXN5721 suspicious?
- Show related fraud activity.
- Explain behaviour anomaly.
- Verify this company.
- Analyze this URL.

AI produces an evidence-based investigation summary.

## 🔒 Privacy Center

- PII masking.
- No raw banking/user data sent to Gemini.
- Secure session cleanup.
- Temporary uploaded files deleted after session.

---

# 🧠 Innovation

FraudSentinel X is **not just a fraud classifier**.

It follows a complete investigation pipeline:

```text
Detect
   ↓
Explain
   ↓
Connect
   ↓
Verify
   ↓
Investigate
   ↓
Human Decision
```

---

# 🏗️ System Architecture

```text
                USER
                  │
                  ▼
          React + Tailwind Dashboard
                  │
                  ▼
            FastAPI Backend
                  │
    ┌─────────────┼────────────────────┐
    │             │                    │
    ▼             ▼                    ▼
 ML Fraud      SHAP AI           ScamShield
 Detection    Explainability      Intelligence
    │             │                    │
    └─────────────┼────────────────────┘
                  ▼
          Evidence Engine
                  ▼
         NetworkX Graph Engine
                  ▼
         Privacy & Sanitization Layer
                  ▼
             MCP Tool Server
                  ▼
            Gemini AI Investigator
                  ▼
       Investigation Summary
                  ▼
          Human Analyst Decision
```

---

# 🧩 Project Workflow

## 1. Fraud Detection

Transaction → ML Model → Risk Score

## 2. Explainability

SHAP identifies top fraud indicators.

## 3. Relationship Analysis

NetworkX finds connected fraud entities.

## 4. ScamShield

URL / Company / Recruiter / Job Verification.

## 5. AI Investigator

Gemini queries MCP tools and summarizes evidence.

## 6. Privacy

Temporary session data deleted when investigation ends.

---

# ⚙️ Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React, Vite, Tailwind CSS |
| Backend | FastAPI (Python) |
| Database | SQLite |
| ML | XGBoost, Isolation Forest, Scikit-learn |
| Explainability | SHAP |
| Graph Analysis | NetworkX |
| AI Assistant | Gemini Flash API |
| AI Tool Layer | MCP (Model Context Protocol) |
| Charts | Recharts |
| Graph UI | React Flow / Cytoscape |
| Threat Intelligence | VirusTotal, Safe Browsing, URLScan, AbuseIPDB |

---

# 🤖 Machine Learning Pipeline

```text
Transaction
    │
    ▼
Feature Engineering
    │
    ▼
Isolation Forest
    │
    ▼
XGBoost Classifier
    │
    ▼
Risk Score
    │
    ▼
SHAP Explanation
    │
    ▼
Fraud Alert
```

---

# 📈 Risk Score

| Score | Risk Level |
|-------|------------|
| 0–29 | Low |
| 30–59 | Medium |
| 60–79 | High |
| 80–100 | Critical |

Example output:

| Risk Factor | Contribution |
|-------------|-------------|
| High Amount | +22 |
| New Device | +18 |
| New Beneficiary | +15 |
| Unusual Time | +10 |
| Location Change | +11 |

**Final Risk Score:** **89/100**

---

# 🛡️ ScamShield Workflow

```text
User enters URL / Company / Job
          │
          ▼
 Threat Intelligence APIs
          │
          ▼
 Domain Analysis
          │
          ▼
 Company Verification (MCA)
          │
          ▼
 Recruiter Verification
          │
          ▼
 NLP Job Scam Detection
          │
          ▼
 Composite Scam Risk Score
```

---

# 🌐 External Verification APIs

| API | Purpose |
|-----|---------|
| VirusTotal | Phishing & malware reputation |
| Google Safe Browsing | Unsafe website detection |
| URLScan | Website behavior analysis |
| AbuseIPDB | Malicious IP reputation |
| MCA Registry | Company registration verification |
| Gemini API | AI Investigator |

> API keys are stored securely using `.env` and never exposed to the frontend.

---

# 🧠 MCP (Model Context Protocol)

MCP connects Gemini AI with backend investigation tools.

### MCP Tools

```text
get_transaction()
get_user_profile()
get_transaction_history()
calculate_behavior_anomaly()
get_risk_factors()
get_related_entities()
search_similar_alerts()

analyze_url()
verify_company()
verify_recruiter()
analyze_job_posting()
generate_investigation_report()
```

### MCP Workflow

```text
Analyst Question
       │
       ▼
Gemini AI
       │
       ▼
MCP Tool Calls
       │
       ▼
FastAPI Backend
       │
       ▼
SQLite + ML + Graph
       │
       ▼
Sanitized Evidence
       │
       ▼
AI Investigation Summary
```

---

# 🔐 Privacy & Security

FraudSentinel X follows **Privacy by Design**.

### Sensitive data never leaves backend

PII is masked before sending context to Gemini.

### Secure Session Cleanup

When user ends session:

- Uploaded files deleted.
- Temporary investigation data removed.
- Cached API responses cleared.
- Session storage cleared.
- Temporary LLM context removed.

Message displayed:

> ✅ Session ended. Temporary investigation data securely deleted.

---

# 📱 Dashboard Screens

## 🖥️ Screen 1 — Fraud Command Center

- Total Transactions
- Fraud Alerts
- High Risk Alerts
- Recent Alerts
- Fraud Trend Charts
- Risk Distribution

## 🔎 Screen 2 — Transaction Investigation

- Transaction Details
- Risk Score
- SHAP Explanation
- Behaviour Anomaly
- Timeline
- Related Entities
- Evidence Panel

## 🤖 Screen 3 — AI Investigator

- Chat Interface
- MCP Tool Activity
- Investigation Summary
- Recommended Next Action

## 🛡️ Screen 4 — ScamShield

- URL Scanner
- Job Scam Analyzer
- Company Verification
- Recruiter Verification

## ⚙️ Screen 5 — Model Working

Visual backend pipeline showing:

Input → Feature Engineering → ML Model → SHAP → Alert.

## 🔒 Screen 6 — Privacy Center

- Privacy Status
- API Security
- Session Cleanup
- End Secure Session

---

# 🗄️ Database Schema

```text
users
transactions
alerts
evidence
relationships
investigation_sessions
investigation_events
url_analysis
company_verifications
job_analysis
```

---

# 🔌 Backend APIs

## Fraud APIs

```http
POST /api/fraud/predict
GET  /api/transactions/{id}
GET  /api/transactions/{id}/risk
GET  /api/transactions/{id}/explanation
GET  /api/transactions/{id}/graph
```

## ScamShield APIs

```http
POST /api/url/analyze
POST /api/job/analyze
POST /api/company/verify
POST /api/recruiter/verify
```

## AI Investigator APIs

```http
POST /api/investigate
POST /api/session/end
GET  /api/model/explanation/{id}
```

---

# 📂 Project Structure

```text
FraudSentinel-X
│
├── frontend/                 # React + Tailwind Dashboard
│
├── backend/
│   ├── app.py
│   ├── database.py
│   ├── models.py
│   ├── routes/
│   └── services/
│
├── ml/
│   ├── fraud_model.py
│   ├── anomaly_model.py
│   ├── shap_explainer.py
│   └── evaluation.py
│
├── scamshield/
│   ├── url_scanner.py
│   ├── company_verifier.py
│   ├── recruiter_verifier.py
│   └── job_analyzer.py
│
├── mcp_server/
│   ├── server.py
│   ├── tools.py
│   ├── investigator.py
│   └── prompts.py
│
├── graph/
│   └── relationship_graph.py
│
├── database/
│   └── fraudsentinel.db
│
├── datasets/
│
├── docs/
│
├── .env.example
├── requirements.txt
└── README.md
```

---

# 🧪 Model Evaluation

Evaluate using:

- Precision
- Recall
- F1 Score
- PR-AUC
- Confusion Matrix
- False Positive Rate

Fraud datasets are imbalanced, so **accuracy is not the primary metric**.

---

# 👥 Team Roles

| Member | Responsibility |
|--------|----------------|
| **Member 1** | AI/ML, Fraud Detection, SHAP, Evaluation |
| **Member 2** | FastAPI Backend, SQLite, APIs, Session Cleanup |
| **Member 3** | React Dashboard, Charts, Privacy Center, Model UI |
| **Member 4** | ScamShield, URL APIs, MCA Verification, Recruiter Verification |
| **Member 5** | MCP Server, Gemini AI Investigator, NetworkX Graph, Integration |

---

# ⏰ 24-Hour Hackathon Plan

| Phase | Deliverable |
|-------|-------------|
| **0–6 Hours** | Dataset, Backend Setup, UI Skeleton |
| **6–12 Hours** | ML Model, APIs, ScamShield Modules |
| **12–18 Hours** | MCP, Gemini Integration, Graph Analysis |
| **18–22 Hours** | Dashboard Integration, Testing |
| **22–24 Hours** | Demo Flow, Pitch, Bug Fixes |

---

# 🎥 Demo Flow

1. User uploads or selects a transaction.
2. AI detects fraud and generates a Risk Score.
3. SHAP explains the decision.
4. NetworkX shows connected entities.
5. User scans a suspicious URL.
6. ScamShield checks phishing and malware indicators.
7. Company verification checks MCA registration.
8. AI Investigator answers questions using MCP.
9. User ends session.
10. Temporary investigation data is securely deleted.

---

# 🌟 Future Scope

- Real-time UPI transaction monitoring.
- SMS & WhatsApp scam detection.
- Voice phishing detection.
- QR code scam detection.
- Browser extension for phishing alerts.
- Android application.
- Enterprise SOC dashboard.
- Multi-language scam detection.
- Real-time bank integration.
- Advanced Graph Neural Networks (future).

---

# 🏆 Why Sentinel X?

Sentinel X is more than a fraud classifier—it is a complete **AI-powered fraud investigation ecosystem**.

### Core Innovation

- 🤖 AI detects suspicious activity.
- 📊 SHAP explains every prediction.
- 🕸️ NetworkX connects fraud entities.
- 🌐 Threat Intelligence verifies URLs and domains.
- 🏢 MCA verifies company registration.
- 👔 Recruiter verification detects impersonation.
- 🧠 MCP enables secure AI investigation.
- 🔒 Privacy layer protects user data.
- 👨‍💻 Human analyst makes the final decision.

---

## ❤️ Built for AI Hackathon 2026

**FraudSentinel X — Detect. Explain. Investigate. Protect.**
