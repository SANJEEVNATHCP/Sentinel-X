from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Automatically initialize SQLite database tables on startup
    init_db()
    yield


app = FastAPI(
    title="FraudSentinel X API",
    description="Backend API for FraudSentinel X prototype.",
    version="0.1.0",
    lifespan=lifespan,
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
# Routers Registration
# ---------------------------------------------------------
from backend.api.transactions import router as transactions_router
from backend.api.scamshield import router as scamshield_router

app.include_router(transactions_router)
app.include_router(scamshield_router)



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
