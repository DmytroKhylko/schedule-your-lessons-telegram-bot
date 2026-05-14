from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.schedule import Schedule
from src.models.schedule_assignment import ScheduleAssignment


class ScheduleRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, schedule_id: int) -> Schedule | None:
        result = await self.session.execute(
            select(Schedule)
            .options(selectinload(Schedule.assignments).selectinload(ScheduleAssignment.user))
            .where(Schedule.id == schedule_id)
        )
        return result.scalar_one_or_none()

    async def get_all_upcoming(self, from_time: datetime) -> list[Schedule]:
        result = await self.session.execute(
            select(Schedule)
            .options(selectinload(Schedule.assignments).selectinload(ScheduleAssignment.user))
            .where(Schedule.starts_at >= from_time, Schedule.is_cancelled.is_(False))
            .order_by(Schedule.starts_at)
        )
        return list(result.scalars().all())

    async def get_upcoming_for_user(self, user_id: int, from_time: datetime) -> list[Schedule]:
        result = await self.session.execute(
            select(Schedule)
            .join(ScheduleAssignment, ScheduleAssignment.schedule_id == Schedule.id)
            .where(
                ScheduleAssignment.user_id == user_id,
                Schedule.starts_at >= from_time,
                Schedule.is_cancelled.is_(False),
            )
            .options(selectinload(Schedule.assignments).selectinload(ScheduleAssignment.user))
            .order_by(Schedule.starts_at)
        )
        return list(result.scalars().all())

    async def get_all_with_recurrence(self) -> list[Schedule]:
        result = await self.session.execute(
            select(Schedule).where(
                Schedule.recurrence_rule.isnot(None),
                Schedule.is_cancelled.is_(False),
            )
        )
        return list(result.scalars().all())

    async def create(
        self,
        title: str,
        starts_at: datetime,
        duration_minutes: int,
        created_by_user_id: int,
        subject: str | None = None,
        location: str | None = None,
        recurrence_rule: str | None = None,
    ) -> Schedule:
        schedule = Schedule(
            title=title,
            subject=subject,
            location=location,
            starts_at=starts_at,
            duration_minutes=duration_minutes,
            recurrence_rule=recurrence_rule,
            created_by_user_id=created_by_user_id,
        )
        self.session.add(schedule)
        await self.session.flush()
        await self.session.refresh(schedule)
        return schedule

    async def cancel(self, schedule: Schedule) -> Schedule:
        schedule.is_cancelled = True
        await self.session.flush()
        return schedule
