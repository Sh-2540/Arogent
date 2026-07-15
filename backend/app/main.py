"""
Arogent API — entrypoint.

This is a decision-support system for community diabetes screening.
It never claims to diagnose disease or verify/prove a screening is
genuine — it estimates a Screening Confidence Score (Arogent Verify)
and, only for high-enough-confidence records, a diabetes risk score
(Arogent Risk). A clinician always makes the final call.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app.models import User, Patient, Screening, Referral  # noqa: F401 — registers tables with Base.metadata
from app.routers import auth, patients, screenings, referrals, dashboard

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("arogent")

_DEFAULT_SECRET_KEY = "dev-secret-key-change-in-production"


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)

    # Critical pre-deployment check: JWTs signed with the default secret
    # (visible in this public codebase) can be forged for any user/role.
    # This is a warning, not a hard failure, so local development and
    # hackathon demos still work without requiring a .env file — but it's
    # loud and impossible to miss in the startup logs.
    if settings.secret_key == _DEFAULT_SECRET_KEY:
        logger.warning(
            "SECURITY WARNING: SECRET_KEY is still the default development value. "
            "JWTs signed with this key can be forged by anyone who has read this "
            "codebase. Set a unique SECRET_KEY environment variable before "
            "deploying anywhere other than local development."
        )

    logger.info(f"{settings.app_name} started — database: {settings.database_url}")
    yield
    logger.info(f"{settings.app_name} shutting down")


app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["health"], summary="Service info", description="Basic service identification — used to confirm the API is reachable.")
def root():
    return {
        "service": settings.app_name,
        "status": "ok",
    }


@app.get("/health", tags=["health"], summary="Health check", description="Liveness check for uptime monitoring and container orchestration.")
def health_check():
    return {"status": "healthy"}


app.include_router(auth.router, prefix=settings.api_v1_prefix)
app.include_router(patients.router, prefix=settings.api_v1_prefix)
app.include_router(screenings.router, prefix=settings.api_v1_prefix)
app.include_router(referrals.router, prefix=settings.api_v1_prefix)
app.include_router(dashboard.router, prefix=settings.api_v1_prefix)

# Roadmap note: for production throughput, screening submission (Arogent
# Verify + Arogent Risk) could move to an asynchronous task queue (e.g.
# Celery/RQ) so the API responds immediately and the pipeline runs in the
# background. Synchronous processing is intentionally kept for the
# hackathon MVP — the pipeline is fast enough that async isn't needed yet,
# and it keeps the demo simple to reason about.
