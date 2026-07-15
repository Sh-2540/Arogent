"""
Screening model — the central record of the whole pipeline.

One row = one diabetes screening event. It stores:
  1. The raw clinical inputs an ASHA worker collects
  2. Arogent Verify's output (Screening Confidence Score + the four
     signal sub-scores that produced it, so the breakdown is auditable)
  3. Arogent Risk's output (only populated when confidence is high
     enough — see app.ai.confidence_engine in Module 3)
  4. Referral lifecycle, once a HIGH risk result triggers one

Keeping all of this on one row (rather than splitting into separate
ScreeningResult / Referral tables) keeps the MVP simple to query for
the Result screen and the District Dashboard. If this grows past the
hackathon, Referral would likely split out into its own table.
"""
from datetime import datetime, timezone

from sqlalchemy import String, Float, DateTime, ForeignKey, JSON, Boolean, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.core.enums import ConfidenceStatus, RiskLevel, ReferralStatus


class Screening(Base):
    __tablename__ = "screenings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), nullable=False, index=True)
    recorded_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    # --- Raw clinical inputs, collected by the ASHA worker ---
    blood_glucose_mg_dl: Mapped[float] = mapped_column(Float, nullable=False)
    bmi: Mapped[float] = mapped_column(Float, nullable=False)
    family_history_diabetes: Mapped[bool] = mapped_column(Boolean, default=False)
    physical_activity_level: Mapped[str] = mapped_column(String(20), nullable=False)  # LOW / MODERATE / HIGH
    symptoms: Mapped[list[str]] = mapped_column(JSON, default=list)  # e.g. ["fatigue", "frequent_urination"]

    # --- Context used by Arogent Verify's consistency signals ---
    village_at_screening: Mapped[str] = mapped_column(String(120), nullable=False)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    screened_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), index=True
    )

    # --- Arogent Verify output ---
    clinical_consistency_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    historical_consistency_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    behaviour_consistency_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    geographic_consistency_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)  # weighted average, 0-100
    confidence_status: Mapped[ConfidenceStatus | None] = mapped_column(
        SAEnum(ConfidenceStatus), nullable=True
    )
    confidence_reasons: Mapped[list[str]] = mapped_column(JSON, default=list)  # human-readable explanation bullets

    # --- Arogent Risk output (only set if confidence_status is HIGH or MEDIUM) ---
    risk_score: Mapped[float | None] = mapped_column(Float, nullable=True)  # 0-100
    risk_level: Mapped[RiskLevel | None] = mapped_column(SAEnum(RiskLevel), nullable=True)

    # --- Referral lifecycle (only set if risk_level is HIGH) ---
    referral_status: Mapped[ReferralStatus | None] = mapped_column(SAEnum(ReferralStatus), nullable=True)
    referred_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # --- Follow-up / demand-side reminder tracking (Section 8b of the proposal) ---
    reminder_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    reminder_sent_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    patient: Mapped["Patient"] = relationship(back_populates="screenings")
    recorded_by: Mapped["User"] = relationship(back_populates="screenings")

    def __repr__(self) -> str:
        return (
            f"<Screening id={self.id} patient_id={self.patient_id} "
            f"confidence_status={self.confidence_status} risk_level={self.risk_level}>"
        )
