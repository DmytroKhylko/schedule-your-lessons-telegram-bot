import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.domain.enums import EventStatus, EventType
from src.models.scheduled_event import ScheduledEvent
from src.queue.redis_event_queue import RedisEventQueue
from src.repositories.scheduled_event_repository import ScheduledEventRepository

logger = logging.getLogger(__name__)


class EventProcessor:
    def __init__(
        self,
        event_queue: RedisEventQueue,
        session_factory: async_sessionmaker[AsyncSession],
        bot: Bot,
    ) -> None:
        self.event_queue = event_queue
        self.session_factory = session_factory
        self.bot = bot

    async def process_due_events(self) -> None:
        event_ids = await self.event_queue.pop_due_event_ids()
        for event_id in event_ids:
            await self._process_single_event(event_id)

    async def _process_single_event(self, event_id: int) -> None:
        async with self.session_factory() as session:
            repository = ScheduledEventRepository(session)
            event = await repository.get_by_id(event_id)

            if not event or event.status != EventStatus.PENDING:
                return

            await repository.mark_processing(event)
            await session.commit()

            try:
                await self._dispatch(event)
                await repository.mark_done(event)
            except Exception:
                logger.exception("Failed to process event %d", event_id)
                await repository.mark_failed(event)

            await session.commit()

    async def _dispatch(self, event: ScheduledEvent) -> None:
        if event.event_type == EventType.LESSON_REMINDER:
            await self._send_lesson_reminder(event.payload)
        elif event.event_type == EventType.NEW_ASSIGNMENT:
            await self._send_new_assignment(event.payload)

    async def _send_lesson_reminder(self, payload: dict) -> None:
        from src.queue.i18n_helper import get_translated_text

        user_telegram_id = payload["user_telegram_id"]
        locale = payload.get("user_language", "uk")
        timezone_str = payload.get("user_timezone", "Europe/Kyiv")
        starts_at = datetime.fromisoformat(payload["starts_at"]).astimezone(ZoneInfo(timezone_str))
        title = payload["schedule_title"]
        duration = payload["duration_minutes"]
        location = payload.get("schedule_location") or ""
        subject = payload.get("schedule_subject") or ""
        minutes_before = payload.get("minutes_before", 60)

        subject_line = get_translated_text(locale, "notification-subject-line", subject=subject) if subject else ""
        location_line = get_translated_text(locale, "notification-location-line", location=location) if location else ""

        text = get_translated_text(
            locale,
            "lesson-reminder",
            title=title,
            subject_line=subject_line,
            date=starts_at.strftime("%d.%m.%Y"),
            time=starts_at.strftime("%H:%M"),
            duration=str(duration),
            location_line=location_line,
            minutes_before=str(minutes_before),
        )
        await self.bot.send_message(user_telegram_id, text)

    async def _send_new_assignment(self, payload: dict) -> None:
        from src.queue.i18n_helper import get_translated_text

        user_telegram_id = payload["user_telegram_id"]
        locale = payload.get("user_language", "uk")
        timezone_str = payload.get("user_timezone", "Europe/Kyiv")
        starts_at = datetime.fromisoformat(payload["starts_at"]).astimezone(ZoneInfo(timezone_str))
        title = payload["schedule_title"]
        duration = payload["duration_minutes"]
        location = payload.get("schedule_location") or ""
        subject = payload.get("schedule_subject") or ""

        subject_line = get_translated_text(locale, "notification-subject-line", subject=subject) if subject else ""
        location_line = get_translated_text(locale, "notification-location-line", location=location) if location else ""

        text = get_translated_text(
            locale,
            "new-assignment",
            title=title,
            subject_line=subject_line,
            date=starts_at.strftime("%d.%m.%Y"),
            time=starts_at.strftime("%H:%M"),
            duration=str(duration),
            location_line=location_line,
        )
        await self.bot.send_message(user_telegram_id, text)
