import logging

from aiogram import Bot

from src.models.schedule import Schedule
from src.models.user import User
from src.notifications.sender import send_new_assignment

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    async def send_new_assignment_notification(
        self, user: User, schedule: Schedule
    ) -> None:
        try:
            await send_new_assignment(self.bot, user, schedule)
            logger.info(
                "Sent new assignment notification to user %d for schedule %d",
                user.telegram_id, schedule.id,
            )
        except Exception:
            logger.exception(
                "Failed to send assignment notification to user %d for schedule %d",
                user.telegram_id, schedule.id,
            )
