from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.enums import NotificationType
from src.models.notification_log import NotificationLog


class NotificationLogRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def exists(
        self,
        user_id: int,
        schedule_id: int,
        occurrence_time: datetime,
        notification_type: NotificationType,
    ) -> bool:
        result = await self.session.execute(
            select(NotificationLog.id).where(
                NotificationLog.user_id == user_id,
                NotificationLog.schedule_id == schedule_id,
                NotificationLog.occurrence_time == occurrence_time,
                NotificationLog.notification_type == notification_type,
            )
        )
        return result.scalar_one_or_none() is not None

    async def create(
        self,
        user_id: int,
        schedule_id: int,
        occurrence_time: datetime,
        notification_type: NotificationType,
    ) -> NotificationLog:
        log = NotificationLog(
            user_id=user_id,
            schedule_id=schedule_id,
            occurrence_time=occurrence_time,
            notification_type=notification_type,
        )
        self.session.add(log)
        await self.session.flush()
        return log
