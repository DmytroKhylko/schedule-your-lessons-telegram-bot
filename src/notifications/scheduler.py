import asyncio
import logging
from datetime import datetime, timedelta, timezone

from aiogram import Bot
from dateutil.rrule import rrulestr
import sqlalchemy as sa
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import selectinload

from src.domain.enums import NotificationType
from src.models.schedule import Schedule
from src.models.schedule_assignment import ScheduleAssignment
from src.notifications.sender import send_lesson_reminder
from src.repositories.notification_log_repository import NotificationLogRepository

logger = logging.getLogger(__name__)

UTC = timezone.utc


class ReminderScheduler:
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        bot: Bot,
        poll_interval_seconds: float = 60.0,
        lookahead_hours: int = 24,
    ) -> None:
        self.session_factory = session_factory
        self.bot = bot
        self.poll_interval_seconds = poll_interval_seconds
        self.lookahead_hours = lookahead_hours
        self._task: asyncio.Task | None = None

    def start(self) -> None:
        self._task = asyncio.create_task(self._run(), name="reminder_scheduler")
        logger.info("Reminder scheduler started (interval=%ss)", self.poll_interval_seconds)

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Reminder scheduler stopped")

    async def _run(self) -> None:
        while True:
            try:
                await self._check_and_send_reminders()
            except Exception:
                logger.exception("Error in reminder scheduler")
            await asyncio.sleep(self.poll_interval_seconds)

    async def _check_and_send_reminders(self) -> None:
        now = datetime.now(tz=UTC)
        lookahead_end = now + timedelta(hours=self.lookahead_hours)

        async with self.session_factory() as session:
            notification_log_repository = NotificationLogRepository(session)

            schedules = await self._get_active_schedules(session, now, lookahead_end)

            for schedule in schedules:
                occurrence_times = self._expand_occurrences(schedule.starts_at, schedule.recurrence_rule, now, lookahead_end)

                for occurrence_time in occurrence_times:
                    for assignment in schedule.assignments:
                        user = assignment.user
                        reminder_time = occurrence_time - timedelta(minutes=user.notification_minutes_before)

                        if reminder_time > now:
                            continue

                        if occurrence_time <= now:
                            continue

                        already_sent = await notification_log_repository.exists(
                            user_id=user.id,
                            schedule_id=schedule.id,
                            occurrence_time=occurrence_time,
                            notification_type=NotificationType.LESSON_REMINDER,
                        )
                        if already_sent:
                            continue

                        await session.refresh(schedule, attribute_names=["is_cancelled"])
                        if schedule.is_cancelled:
                            break

                        try:
                            await send_lesson_reminder(self.bot, user, schedule, occurrence_time)
                            await notification_log_repository.create(
                                user_id=user.id,
                                schedule_id=schedule.id,
                                occurrence_time=occurrence_time,
                                notification_type=NotificationType.LESSON_REMINDER,
                            )
                            await session.commit()
                            logger.info(
                                "Sent lesson reminder to user %d for schedule %d at %s",
                                user.telegram_id, schedule.id, occurrence_time,
                            )
                        except Exception:
                            await session.rollback()
                            logger.exception(
                                "Failed to send reminder to user %d for schedule %d",
                                user.telegram_id, schedule.id,
                            )
                            return

    async def _get_active_schedules(
        self,
        session: AsyncSession,
        now: datetime,
        lookahead_end: datetime,
    ) -> list[Schedule]:
        result = await session.execute(
            select(Schedule)
            .options(selectinload(Schedule.assignments).selectinload(ScheduleAssignment.user))
            .where(
                Schedule.is_cancelled.is_(False),
                sa.or_(
                    sa.and_(Schedule.starts_at > now, Schedule.starts_at <= lookahead_end),
                    Schedule.recurrence_rule.isnot(None),
                ),
            )
        )
        return list(result.scalars().all())

    def _expand_occurrences(
        self,
        starts_at: datetime,
        recurrence_rule: str | None,
        window_start: datetime,
        window_end: datetime,
    ) -> list[datetime]:
        if not recurrence_rule:
            if window_start <= starts_at <= window_end:
                return [starts_at]
            return []

        try:
            rule = rrulestr(recurrence_rule, dtstart=starts_at)
            return list(rule.between(window_start, window_end, inc=True))
        except Exception:
            logger.exception("Failed to expand recurrence rule: %s", recurrence_rule)
            if window_start <= starts_at <= window_end:
                return [starts_at]
            return []
