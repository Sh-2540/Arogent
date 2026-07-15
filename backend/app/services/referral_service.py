"""Referral service — lookup and status transitions (PENDING -> REFERRED -> COMPLETED)."""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.referral import Referral
from app.core.enums import ReferralStatus


def list_referrals(db: Session, status_filter: ReferralStatus | None = None, limit: int = 50) -> list[Referral]:
    query = db.query(Referral)
    if status_filter:
        query = query.filter(Referral.status == status_filter)
    return query.order_by(Referral.generated_at.desc()).limit(limit).all()


def get_referral(db: Session, referral_id: int) -> Referral | None:
    return db.get(Referral, referral_id)


def update_referral_status(db: Session, referral_id: int, new_status: ReferralStatus) -> Referral | None:
    referral = get_referral(db, referral_id)
    if referral is None:
        return None
    referral.status = new_status
    db.commit()
    db.refresh(referral)
    return referral
