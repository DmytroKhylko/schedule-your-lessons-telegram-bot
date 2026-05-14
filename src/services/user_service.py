from src.domain.enums import RoleType, UserStatus
from src.models.user import User
from src.repositories.role_repository import RoleRepository
from src.repositories.user_repository import UserRepository


class UserService:
    def __init__(
        self,
        user_repository: UserRepository,
        role_repository: RoleRepository,
    ) -> None:
        self.user_repository = user_repository
        self.role_repository = role_repository

    async def register_or_get(
        self,
        telegram_id: int,
        username: str | None,
        full_name: str,
        language_code: str,
        timezone: str,
    ) -> tuple[User, bool]:
        user = await self.user_repository.get_by_telegram_id(telegram_id)
        if user:
            return user, False
        user = await self.user_repository.create(
            telegram_id=telegram_id,
            username=username,
            full_name=full_name,
            language_code=language_code,
            timezone=timezone,
        )
        return user, True

    async def ensure_admin_registered(
        self,
        telegram_id: int,
        username: str | None,
        full_name: str,
        language_code: str,
        timezone: str,
    ) -> User:
        user = await self.user_repository.get_by_telegram_id(telegram_id)
        if not user:
            user = await self.user_repository.create(
                telegram_id=telegram_id,
                username=username,
                full_name=full_name,
                language_code=language_code,
                timezone=timezone,
            )
        if user.status != UserStatus.ACTIVE:
            user = await self.user_repository.update_status(user, UserStatus.ACTIVE)
        existing_roles = {role.role_type for role in user.roles}
        if RoleType.ADMIN not in existing_roles:
            await self.role_repository.add_role(user.id, RoleType.ADMIN)
        return user

    async def approve(self, user: User, role_type: RoleType) -> User:
        user = await self.user_repository.update_status(user, UserStatus.ACTIVE)
        existing_roles = {role.role_type for role in user.roles}
        if role_type not in existing_roles:
            await self.role_repository.add_role(user.id, role_type)
        return user

    async def reject(self, user: User) -> User:
        return await self.user_repository.update_status(user, UserStatus.REJECTED)

    async def update_language(self, user: User, language_code: str) -> User:
        return await self.user_repository.update_language(user, language_code)

    async def update_timezone(self, user: User, timezone: str) -> User:
        return await self.user_repository.update_timezone(user, timezone)

    async def update_notification_minutes_before(self, user: User, minutes: int) -> User:
        return await self.user_repository.update_notification_minutes_before(user, minutes)

    async def get_pending_users(self) -> list[User]:
        return await self.user_repository.get_pending()

    async def get_all_assignable_users(self) -> list[User]:
        return await self.user_repository.get_all_active()
