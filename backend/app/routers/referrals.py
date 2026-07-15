"""Referral routes — view and update referral status. Business logic lives
in app.services.referral_service."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.enums import UserRole, ReferralStatus
from app.core.security import get_current_user, require_roles
from app.models.user import User
from app.schemas.referral import ReferralRead, ReferralStatusUpdate
from app.services.referral_service import list_referrals, update_referral_status

router = APIRouter(prefix="/referrals", tags=["referrals"])


@router.get(
    "",
    response_model=list[ReferralRead],
    summary="List referrals",
    description="Lists referrals, optionally filtered by status — used by the PHC officer's queue and the district dashboard.",
)
def read_referrals(
    status_filter: ReferralStatus | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[ReferralRead]:
    referrals = list_referrals(db, status_filter=status_filter)
    return [ReferralRead.model_validate(r) for r in referrals]


@router.patch(
    "/{referral_id}",
    response_model=ReferralRead,
    summary="Update a referral's status",
    description="Moves a referral through PENDING -> REFERRED -> COMPLETED. Only PHC officers may update referral status.",
    dependencies=[Depends(require_roles(UserRole.PHC_OFFICER))],
    responses={404: {"description": "Referral not found"}},
)
def patch_referral_status(
    referral_id: int,
    data: ReferralStatusUpdate,
    db: Session = Depends(get_db),
) -> ReferralRead:
    referral = update_referral_status(db, referral_id, data.status)
    if referral is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Referral {referral_id} not found")
    return ReferralRead.model_validate(referral)
