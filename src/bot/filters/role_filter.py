from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery, Message

from config import Settings
from src.domain.enums import RoleType, UserStatus
from src.models.user import User


class AdminFilter(BaseFilter):
    async def __call__(
        self,
        event: Message | CallbackQuery,
        settings: Settings,
        current_user: User | None = None,
    ) -> bool:
        from_user = event.from_user if isinstance(event, Message) else event.from_user
        if not from_user:
            return False
        if from_user.id in settings.admin_telegram_ids:
            return True
        if not current_user:
            return False
        return any(role.role_type == RoleType.ADMIN for role in current_user.roles)


class ActiveUserFilter(BaseFilter):
    async def __call__(self, event: Message | CallbackQuery, current_user: User | None = None) -> bool:
        return current_user is not None and current_user.status == UserStatus.ACTIVE
