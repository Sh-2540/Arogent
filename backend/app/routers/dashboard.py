"""Dashboard route — District Health Officer's aggregate view. Only
District Officers may access it; aggregation logic lives in
app.services.dashboard_service."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.enums import UserRole
from app.core.security import require_roles
from app.schemas.dashboard import DashboardSummary
from app.services.dashboard_service import get_dashboard_summary

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get(
    "",
    response_model=DashboardSummary,
    summary="Get the district dashboard summary",
    description=(
        "Aggregate screening coverage, confidence/risk distributions, pending "
        "referrals, and per-village breakdowns for the District Health Officer's "
        "view (Arogent Map)."
    ),
    dependencies=[Depends(require_roles(UserRole.DISTRICT_OFFICER))],
)
def read_dashboard(db: Session = Depends(get_db)) -> DashboardSummary:
    return get_dashboard_summary(db)
