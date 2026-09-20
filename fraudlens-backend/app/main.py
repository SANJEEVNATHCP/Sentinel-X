"""
FraudLens AI - Main Application Entrypoint
"See the Risk. Understand the Evidence. Act Safely."
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.database import engine, Base, SessionLocal
from app.logging_config import logger
from app.middleware import RequestTracingMiddleware
from app.exceptions import FraudLensException, AuthenticationError, NotFoundError, ValidationError, SSRFSecurityError
from app.schemas.common import ErrorResponse, ResponseMetadata
from app.utils.timestamps import utc_now_iso

def _find_frontend_dir() -> str:
    candidates = [
        os.environ.get("FRONTEND_DIR"),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend")),
        "/app/frontend",
        "/app",
        os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    ]
    for c in candidates:
        if c and os.path.exists(os.path.join(c, "index.html")):
            return c
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

FRONTEND_DIR = _find_frontend_dir()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initializes local tables and seed data if using SQLite development database."""
    Base.metadata.create_all(bind=engine)
    logger.info(f"{settings.APP_NAME} v{settings.APP_VERSION} initialized in {settings.ENVIRONMENT} mode.")
    
    # Auto-seed datasets into database if empty
    try:
        from scripts.seed_database import auto_seed_if_empty
        db = SessionLocal()
        try:
            auto_seed_if_empty(db)
        finally:
            db.close()
    except Exception as e:
        logger.warning(f"Startup auto-seed skipped: {str(e)}")
    yield

# API Routers
from app.api.auth import router as auth_router
from app.api.dashboard import router as dashboard_router
from app.api.transactions import router as transactions_router
from app.api.company import router as company_router
from app.api.scam import router as scam_router
from app.api.investigations import router as investigations_router
from app.api.results import router as results_router
from app.api.profile import router as profile_router
from app.api.privacy import router as privacy_router
from app.api.health import router as health_router

# Initialize FastAPI Application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Explainable fraud intelligence platform that analyzes transactions, URLs, companies, recruiters, and offer letters.",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:[0-9]+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Request Tracing & Security Headers
app.add_middleware(RequestTracingMiddleware)

# Custom Domain Exception Handlers
@app.exception_handler(FraudLensException)
async def fraudlens_exception_handler(request: Request, exc: FraudLensException):
    req_id = getattr(request.state, "request_id", None)
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            message=exc.message,
            error_code=exc.error_code,
            metadata=ResponseMetadata(request_id=req_id)
        ).model_dump()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    req_id = getattr(request.state, "request_id", None)
    logger.error(f"Unhandled error processing request: {str(exc)}", extra={"request_id": req_id})
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            message="An unexpected server error occurred. Please retry shortly.",
            error_code="INTERNAL_SERVER_ERROR",
            metadata=ResponseMetadata(request_id=req_id)
        ).model_dump()
    )

# Include API Routers
app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(transactions_router)
app.include_router(company_router)
app.include_router(scam_router)
app.include_router(investigations_router)
app.include_router(results_router)
app.include_router(profile_router)
app.include_router(privacy_router)
app.include_router(health_router)

# Mount frontend static assets if present
css_path = os.path.join(FRONTEND_DIR, "css")
js_path = os.path.join(FRONTEND_DIR, "js")
if os.path.exists(css_path):
    app.mount("/css", StaticFiles(directory=css_path), name="css")
if os.path.exists(js_path):
    app.mount("/js", StaticFiles(directory=js_path), name="js")

@app.get("/", tags=["Root"])
@app.get("/login", tags=["Frontend SPA"])
@app.get("/register", tags=["Frontend SPA"])
@app.get("/dashboard", tags=["Frontend SPA"])
@app.get("/upi", tags=["Frontend SPA"])
@app.get("/scam", tags=["Frontend SPA"])
@app.get("/results", tags=["Frontend SPA"])
@app.get("/profile", tags=["Frontend SPA"])
def root_endpoint(request: Request):
    """Serves the web application or returns API metadata if requested programmatically."""
    accept = request.headers.get("accept", "")
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "name": settings.APP_NAME,
        "tagline": "See the Risk. Understand the Evidence. Act Safely.",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/api/health",
        "web_app": "/"
    }

# ===================================================
# Chrome Extension Compatibility Endpoints
# ===================================================
from fastapi.responses import HTMLResponse
from app.utils.url_utils import extract_domain
from app.services.mca_service import MCAService
from app.services.spam_dataset_service import SpamDatasetService

@app.post("/api/check-url", tags=["Extension Adapter"])
async def extension_check_url(request: Request):
    """
    Direct adapter for ScamShield Chrome extension requests.
    Checks against Company Master dataset (Active vs Inactive) and threat feeds.
    """
    data = {}
    try:
        data = await request.json()
    except Exception:
        pass

    raw_url = data.get("url", "")
    raw_domain = data.get("domain", "")
    domain = extract_domain(raw_url or raw_domain)

    if not domain:
        return JSONResponse(
            status_code=400,
            content={
                "found": False,
                "risk_score": 0,
                "risk_level": "UNKNOWN",
                "reason": "Invalid or empty domain provided",
                "domain": ""
            }
        )

    db = SessionLocal()
    try:
        # 1. Check Company Master dataset
        mca_res = MCAService.verify_company(db, "", domain)
        if mca_res.get("mca_verified"):
            c_status = mca_res.get("company_status", "UNKNOWN").upper()
            if c_status in ["INACTIVE", "DORMANT", "STRUCK OFF", "DISSOLVED", "CLOSED"]:
                return {
                    "found": True,
                    "risk_score": 90,
                    "risk_level": "HIGH",
                    "status": "Inactive",
                    "company_status": "Inactive",
                    "company_name": mca_res.get("company_name"),
                    "cin": mca_res.get("cin"),
                    "source": "sample.xlsx (Company Master Dataset)",
                    "reason": f"Company '{mca_res.get('company_name')}' is marked as INACTIVE in dataset (sample.xlsx). Caution: Website or company may be defunct or unauthorized.",
                    "domain": domain
                }
            else:
                return {
                    "found": False,
                    "verified_active": True,
                    "status": "Active",
                    "company_status": "Active",
                    "company_name": mca_res.get("company_name"),
                    "cin": mca_res.get("cin"),
                    "risk_level": "LOW",
                    "risk_score": 0,
                    "source": "sample.xlsx (Company Master Dataset)",
                    "reason": f"Company '{mca_res.get('company_name')}' is verified as ACTIVE in dataset (sample.xlsx).",
                    "domain": domain
                }

        # 2. Check Threat dataset
        threat = SpamDatasetService.lookup_url(db, raw_url or domain)
        if threat.get("found"):
            return {
                "found": True,
                "risk_score": 85 if threat.get("status") == "ACTIVE" else 40,
                "risk_level": "HIGH" if threat.get("status") == "ACTIVE" else "MODERATE",
                "reason": f"Domain found in ScamShield threat dataset ({threat.get('status')})",
                "domain": domain
            }

        # 3. Not found
        return {
            "found": False,
            "risk_score": 0,
            "risk_level": "UNKNOWN",
            "reason": "No known match found in ScamShield dataset",
            "domain": domain
        }
    finally:
        db.close()

@app.get("/analyze", response_class=HTMLResponse, tags=["Extension Adapter"])
def extension_analyze_page(url: str = "No URL provided"):
    """HTML preview page opened by extension's [View Full Analysis] button."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>FraudLens AI — Threat & Dataset Report</title>
  <style>
    body {{
      margin: 0;
      background: #060a14;
      color: #f8fafc;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      padding: 20px;
    }}
    .card {{
      background: #0d1527;
      border: 1px solid #1e293b;
      padding: 30px 40px;
      max-width: 650px;
      border-radius: 12px;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    }}
    h1 {{
      color: #38bdf8;
      margin-top: 0;
      display: flex;
      align-items: center;
      gap: 10px;
    }}
    .url-box {{
      background: #040810;
      border: 1px solid #334155;
      padding: 12px;
      border-radius: 6px;
      font-family: monospace;
      color: #38bdf8;
      word-break: break-all;
      margin: 15px 0;
    }}
    p {{
      color: #94a3b8;
      line-height: 1.6;
    }}
    .btn {{
      display: inline-block;
      margin-top: 20px;
      background: #38bdf8;
      color: #060a14;
      font-weight: bold;
      padding: 10px 20px;
      border-radius: 6px;
      text-decoration: none;
    }}
  </style>
</head>
<body>
  <div class="card">
    <h1>🛡 FraudLens AI Threat Intelligence Report</h1>
    <p>Target domain / URL:</p>
    <div class="url-box">{url}</div>
    <p>This resource was cross-referenced with FraudLens AI corporate catalog and threat feeds.</p>
    <a href="http://127.0.0.1:8000/#/dashboard" class="btn">Open FraudLens Web Workspace →</a>
  </div>
</body>
</html>"""

