from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.enums import EventStatus, EventType
from src.models.scheduled_event import ScheduledEvent


class ScheduledEventRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, event_id: int) -> ScheduledEvent | None:
        result = await self.session.execute(
            select(ScheduledEvent).where(ScheduledEvent.id == event_id)
        )
        return result.scalar_one_or_none()

    async def get_all_pending(self) -> list[ScheduledEvent]:
        result = await self.session.execute(
            select(ScheduledEvent).where(ScheduledEvent.status == EventStatus.PENDING)
        )
        return list(result.scalars().all())

    async def get_pending_for_schedule(self, schedule_id: int) -> list[ScheduledEvent]:
        result = await self.session.execute(
            select(ScheduledEvent).where(
                ScheduledEvent.status == EventStatus.PENDING,
                ScheduledEvent.payload["schedule_id"].astext.cast(int) == schedule_id,
            )
        )
        return list(result.scalars().all())

    async def create(
        self,
        event_type: EventType,
        payload: dict,
        scheduled_for: datetime,
    ) -> ScheduledEvent:
        event = ScheduledEvent(
            event_type=event_type,
            payload=payload,
            scheduled_for=scheduled_for,
        )
        self.session.add(event)
        await self.session.flush()
        await self.session.refresh(event)
        return event

    async def mark_processing(self, event: ScheduledEvent) -> ScheduledEvent:
        event.status = EventStatus.PROCESSING
        await self.session.flush()
        return event

    async def mark_done(self, event: ScheduledEvent) -> ScheduledEvent:
        event.status = EventStatus.DONE
        await self.session.flush()
        return event

    async def mark_failed(self, event: ScheduledEvent) -> ScheduledEvent:
        event.status = EventStatus.FAILED
        await self.session.flush()
        return event

    async def cancel_pending_for_schedule(self, schedule_id: int) -> None:
        events = await self.get_pending_for_schedule(schedule_id)
        for event in events:
            event.status = EventStatus.FAILED
        await self.session.flush()
