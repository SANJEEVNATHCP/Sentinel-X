from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="FraudSentinel X API",
    description="Backend API for FraudSentinel X prototype.",
    version="0.1.0",
)

# ---------------------------------------------------------
# CORS Middleware Configuration
# Configured for local React frontend (Vite :5173, CRA :3000)
# ---------------------------------------------------------
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# Future Module Connections (to be wired in subsequent steps):
# - api/       : Attach API routers (e.g. app.include_router(router, prefix="/api/v1"))
# - database/  : Setup database connection, ORM models, and session dependencies
# - services/  : Business logic layer (ScamShield, ML inference services, etc.)
# - schemas/   : Pydantic request and response schemas
# ---------------------------------------------------------


@app.get("/")
def read_root():
    """Root endpoint returning project info and status."""
    return {
        "project": "FraudSentinel X",
        "status": "online",
        "version": "0.1.0",
        "message": "FraudSentinel X Backend API is running.",
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
    }
