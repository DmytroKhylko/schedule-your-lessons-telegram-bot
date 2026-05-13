from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.schedule_assignment import ScheduleAssignment


class ScheduleAssignmentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_schedule_id(self, schedule_id: int) -> list[ScheduleAssignment]:
        result = await self.session.execute(
            select(ScheduleAssignment)
            .options(selectinload(ScheduleAssignment.user))
            .where(ScheduleAssignment.schedule_id == schedule_id)
        )
        return list(result.scalars().all())

    async def create(self, schedule_id: int, user_id: int) -> ScheduleAssignment:
        assignment = ScheduleAssignment(schedule_id=schedule_id, user_id=user_id)
        self.session.add(assignment)
        await self.session.flush()
        return assignment

    async def delete_by_schedule_id(self, schedule_id: int) -> None:
        result = await self.session.execute(
            select(ScheduleAssignment).where(ScheduleAssignment.schedule_id == schedule_id)
        )
        for assignment in result.scalars().all():
            await self.session.delete(assignment)
        await self.session.flush()
