from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update

from config import Settings
from src.domain.enums import UserStatus
from src.models.user import User
from src.repositories.role_repository import RoleRepository
from src.repositories.user_repository import UserRepository
from src.services.user_service import UserService


class UserContextMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        from_user = None
        if isinstance(event, Update):
            if event.message:
                from_user = event.message.from_user
            elif event.callback_query:
                from_user = event.callback_query.from_user
            elif event.inline_query:
                from_user = event.inline_query.from_user
        else:
            from_user = getattr(event, "from_user", None)

        from sqlalchemy.ext.asyncio import AsyncSession

        session: AsyncSession = data["db_session"]
        settings: Settings = data["settings"]

        current_user: User | None = None

        if from_user:
            user_repository = UserRepository(session)
            role_repository = RoleRepository(session)
            user_service = UserService(user_repository, role_repository)

            tg_lang = from_user.language_code or ""
            locale = "uk" if tg_lang.startswith("uk") else "en"

            if from_user.id in settings.admin_telegram_ids:
                current_user = await user_service.ensure_admin_registered(
                    telegram_id=from_user.id,
                    username=from_user.username,
                    full_name=from_user.full_name,
                    language_code=locale,
                    timezone=settings.default_timezone,
                )
            else:
                current_user = await user_repository.get_by_telegram_id(from_user.id)

        data["current_user"] = current_user
        return await handler(event, data)
