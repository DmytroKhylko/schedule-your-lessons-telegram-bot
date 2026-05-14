from datetime import datetime
from zoneinfo import ZoneInfo

from src.models.schedule import Schedule
from src.models.user import User
from src.repositories.schedule_assignment_repository import ScheduleAssignmentRepository
from src.repositories.schedule_repository import ScheduleRepository


class ScheduleService:
    def __init__(
        self,
        schedule_repository: ScheduleRepository,
        schedule_assignment_repository: ScheduleAssignmentRepository,
    ) -> None:
        self.schedule_repository = schedule_repository
        self.schedule_assignment_repository = schedule_assignment_repository

    async def create_schedule(
        self,
        title: str,
        starts_at: datetime,
        duration_minutes: int,
        created_by: User,
        subject: str | None = None,
        location: str | None = None,
        recurrence_rule: str | None = None,
        participant_ids: list[int] | None = None,
    ) -> Schedule:
        schedule = await self.schedule_repository.create(
            title=title,
            starts_at=starts_at,
            duration_minutes=duration_minutes,
            created_by_user_id=created_by.id,
            subject=subject,
            location=location,
            recurrence_rule=recurrence_rule,
        )
        for user_id in participant_ids or []:
            await self.schedule_assignment_repository.create(schedule.id, user_id)
        return schedule

    async def cancel_schedule(self, schedule: Schedule) -> Schedule:
        return await self.schedule_repository.cancel(schedule)

    async def get_schedule(self, schedule_id: int) -> Schedule | None:
        return await self.schedule_repository.get_by_id(schedule_id)

    async def get_upcoming_schedules(self, from_time: datetime) -> list[Schedule]:
        return await self.schedule_repository.get_all_upcoming(from_time)

    async def get_upcoming_schedules_for_user(
        self, user_id: int, from_time: datetime
    ) -> list[Schedule]:
        return await self.schedule_repository.get_upcoming_for_user(user_id, from_time)

    def localize_starts_at(self, schedule: Schedule, timezone: str) -> datetime:
        return schedule.starts_at.astimezone(ZoneInfo(timezone))
