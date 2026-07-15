"""
User model — covers all three roles (ASHA, PHC_OFFICER, DISTRICT_OFFICER)
in a single table. A hackathon MVP doesn't need separate tables per role;
the `role` column plus role-based access in Module 5 is enough, and it
keeps auth logic simple.
"""
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.core.enums import UserRole


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    username: Mapped[str] = mapped_column(String(80), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole), nullable=False)

    # For ASHA workers and PHC officers, the village/taluka they're assigned to.
    # District officers see the whole taluka, so this can be null for them.
    assigned_village: Mapped[str | None] = mapped_column(String(120), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )

    screenings: Mapped[list["Screening"]] = relationship(back_populates="recorded_by")

    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username!r} role={self.role}>"
