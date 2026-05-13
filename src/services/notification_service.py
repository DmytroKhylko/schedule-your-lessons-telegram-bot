import logging
from datetime import datetime, timedelta, timezone

from dateutil.rrule import rrulestr

from src.domain.enums import EventType
from src.models.schedule import Schedule
from src.models.user import User
from src.queue.redis_event_queue import RedisEventQueue
from src.repositories.schedule_assignment_repository import ScheduleAssignmentRepository
from src.repositories.scheduled_event_repository import ScheduledEventRepository

logger = logging.getLogger(__name__)

UTC = timezone.utc


class NotificationService:
    def __init__(
        self,
        scheduled_event_repository: ScheduledEventRepository,
        schedule_assignment_repository: ScheduleAssignmentRepository,
        event_queue: RedisEventQueue,
        days_ahead: int = 90,
    ) -> None:
        self.scheduled_event_repository = scheduled_event_repository
        self.schedule_assignment_repository = schedule_assignment_repository
        self.event_queue = event_queue
        self.days_ahead = days_ahead

    async def schedule_notifications_for_new_schedule(self, schedule: Schedule) -> None:
        assignments = await self.schedule_assignment_repository.get_by_schedule_id(schedule.id)
        occurrence_times = self._expand_occurrences(schedule)

        for occurrence_time in occurrence_times:
            for assignment in assignments:
                await self._create_reminder_event(assignment.user, schedule, occurrence_time)

    async def schedule_new_assignment_notification(
        self, user: User, schedule: Schedule
    ) -> None:
        event = await self.scheduled_event_repository.create(
            event_type=EventType.NEW_ASSIGNMENT,
            payload={
                "user_telegram_id": user.telegram_id,
                "user_timezone": user.timezone,
                "user_language": user.language_code,
                "schedule_id": schedule.id,
                "schedule_title": schedule.title,
                "schedule_subject": schedule.subject,
                "schedule_location": schedule.location,
                "starts_at": schedule.starts_at.isoformat(),
                "duration_minutes": schedule.duration_minutes,
            },
            scheduled_for=datetime.now(tz=UTC),
        )
        await self.event_queue.add_event(event)

    async def cancel_pending_notifications_for_schedule(self, schedule_id: int) -> None:
        events = await self.scheduled_event_repository.get_pending_for_schedule(schedule_id)
        for event in events:
            await self.scheduled_event_repository.mark_failed(event)
            await self.event_queue.remove_event(event.id)

    async def _create_reminder_event(
        self, user: User, schedule: Schedule, occurrence_time: datetime
    ) -> None:
        notification_time = occurrence_time - timedelta(minutes=user.notification_minutes_before)
        if notification_time <= datetime.now(tz=UTC):
            return

        event = await self.scheduled_event_repository.create(
            event_type=EventType.LESSON_REMINDER,
            payload={
                "user_telegram_id": user.telegram_id,
                "user_timezone": user.timezone,
                "user_language": user.language_code,
                "schedule_id": schedule.id,
                "schedule_title": schedule.title,
                "schedule_subject": schedule.subject,
                "schedule_location": schedule.location,
                "starts_at": occurrence_time.isoformat(),
                "duration_minutes": schedule.duration_minutes,
                "minutes_before": user.notification_minutes_before,
            },
            scheduled_for=notification_time,
        )
        await self.event_queue.add_event(event)

    def _expand_occurrences(self, schedule: Schedule) -> list[datetime]:
        if not schedule.recurrence_rule:
            return [schedule.starts_at]

        end_date = datetime.now(tz=UTC) + timedelta(days=self.days_ahead)
        try:
            rule = rrulestr(schedule.recurrence_rule, dtstart=schedule.starts_at)
            return list(rule.between(datetime.now(tz=UTC), end_date, inc=True))
        except Exception:
            logger.exception(
                "Failed to expand recurrence rule for schedule %d", schedule.id
            )
            return [schedule.starts_at]
