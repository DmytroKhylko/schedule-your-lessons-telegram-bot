from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class ScheduleAssignment(Base):
    __tablename__ = "schedule_assignments"
    __table_args__ = (UniqueConstraint("schedule_id", "user_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    schedule_id: Mapped[int] = mapped_column(
        ForeignKey("schedules.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    schedule: Mapped["Schedule"] = relationship("Schedule", back_populates="assignments")
    user: Mapped["User"] = relationship("User", back_populates="schedule_assignments", lazy="selectin")
