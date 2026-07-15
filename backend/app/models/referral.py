"""
Referral model — an explicit, tangible record generated whenever Arogent
Risk produces a HIGH risk_level, rather than just a status flag on the
Screening row. This is what the Result screen (Module 8) actually displays
and what a PHC officer would act on.
"""
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.core.enums import ReferralStatus


class Referral(Base):
    __tablename__ = "referrals"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), nullable=False, index=True)
    screening_id: Mapped[int] = mapped_column(ForeignKey("screenings.id"), unique=True, nullable=False)

    phc: Mapped[str] = mapped_column(String(150), nullable=False)
    priority: Mapped[str] = mapped_column(String(20), nullable=False)  # mirrors RiskLevel at generation time
    reason: Mapped[str] = mapped_column(String(500), nullable=False)

    status: Mapped[ReferralStatus] = mapped_column(
        SAEnum(ReferralStatus), default=ReferralStatus.PENDING, nullable=False
    )
    generated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )

    patient: Mapped["Patient"] = relationship()
    screening: Mapped["Screening"] = relationship()

    def __repr__(self) -> str:
        return f"<Referral id={self.id} patient_id={self.patient_id} status={self.status}>"
