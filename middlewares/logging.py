import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: Dict[str, Any],
    ) -> Any:
        if isinstance(event, Message):
            user = event.from_user

            logger.info(
                "update=message user_id=%s username=%s text=%r",
                user.id if user else "unknown",
                user.username if user else None,
                event.text,
            )

        elif isinstance(event, CallbackQuery):
            user = event.from_user

            logger.info(
                "update=callback user_id=%s username=%s data=%r",
                user.id if user else "unknown",
                user.username if user else None,
                event.data,
            )

        return await handler(event, data)
