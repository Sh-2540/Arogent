"""
Patient model.

Deliberately minimal for the hackathon MVP — just enough demographic and
contact info to support screening, risk prediction, and SMS/WhatsApp
follow-up. Real government ID linkage (ABHA) is roadmap, not MVP.
"""
from datetime import datetime, date, timezone

from sqlalchemy import String, Integer, Date, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    gender: Mapped[str] = mapped_column(String(20), nullable=False)

    village: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    phone_number: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Used by Arogent Verify's Historical Consistency signal.
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)

    registered_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    registered_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )

    screenings: Mapped[list["Screening"]] = relationship(
        back_populates="patient", order_by="Screening.screened_at"
    )

    def __repr__(self) -> str:
        return f"<Patient id={self.id} full_name={self.full_name!r} village={self.village!r}>"
