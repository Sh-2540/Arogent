"""
Dashboard service — read-only aggregation over Screening and Referral for
the District Health Officer's view (Module 9 consumes this via the
dashboard router). All aggregation logic lives here, not in the router.
"""
from __future__ import annotations

from sqlalchemy import func, Integer
from sqlalchemy.orm import Session

from app.models.screening import Screening
from app.models.referral import Referral
from app.core.enums import ConfidenceStatus, RiskLevel, ReferralStatus
from app.schemas.dashboard import DashboardSummary, StatusCount, VillageSummary


def get_dashboard_summary(db: Session) -> DashboardSummary:
    total_screenings = db.query(func.count(Screening.id)).scalar() or 0

    confidence_counts = (
        db.query(Screening.confidence_status, func.count(Screening.id))
        .group_by(Screening.confidence_status)
        .all()
    )
    screenings_by_confidence_status = [
        StatusCount(status=status.value if status else "UNKNOWN", count=count)
        for status, count in confidence_counts
    ]

    risk_counts = (
        db.query(Screening.risk_level, func.count(Screening.id))
        .filter(Screening.risk_level.isnot(None))
        .group_by(Screening.risk_level)
        .all()
    )
    screenings_by_risk_level = [
        StatusCount(status=level.value, count=count) for level, count in risk_counts
    ]

    pending_referrals_count = (
        db.query(func.count(Referral.id)).filter(Referral.status == ReferralStatus.PENDING).scalar() or 0
    )

    village_rows = (
        db.query(
            Screening.village_at_screening,
            func.count(Screening.id),
            func.sum(func.cast(Screening.risk_level == RiskLevel.HIGH, type_=Integer)),
            func.sum(func.cast(Screening.confidence_status == ConfidenceStatus.NEEDS_REVIEW, type_=Integer)),
            func.avg(Screening.confidence_score),
        )
        .group_by(Screening.village_at_screening)
        .all()
    )
    village_summaries = [
        VillageSummary(
            village=village,
            total_screenings=total,
            high_risk_count=high_risk or 0,
            needs_review_count=needs_review or 0,
            average_confidence_score=round(avg_confidence, 1) if avg_confidence is not None else 0.0,
        )
        for village, total, high_risk, needs_review, avg_confidence in village_rows
    ]

    return DashboardSummary(
        total_screenings=total_screenings,
        screenings_by_confidence_status=screenings_by_confidence_status,
        screenings_by_risk_level=screenings_by_risk_level,
        pending_referrals_count=pending_referrals_count,
        village_summaries=village_summaries,
    )
