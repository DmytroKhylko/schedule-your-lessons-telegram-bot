from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.enums import RoleType, UserStatus
from src.models.role import Role
from src.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        result = await self.session.execute(
            select(User)
            .options(selectinload(User.roles))
            .where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: int) -> User | None:
        result = await self.session.execute(
            select(User).options(selectinload(User.roles)).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_pending(self) -> list[User]:
        result = await self.session.execute(
            select(User).where(User.status == UserStatus.PENDING)
        )
        return list(result.scalars().all())

    async def get_active_with_role(self, role_type: RoleType) -> list[User]:
        result = await self.session.execute(
            select(User)
            .join(Role, Role.user_id == User.id)
            .where(User.status == UserStatus.ACTIVE, Role.role_type == role_type)
            .options(selectinload(User.roles))
        )
        return list(result.scalars().unique().all())

    async def get_all_active(self) -> list[User]:
        result = await self.session.execute(
            select(User)
            .options(selectinload(User.roles))
            .where(User.status == UserStatus.ACTIVE)
        )
        return list(result.scalars().all())

    async def create(
        self,
        telegram_id: int,
        username: str | None,
        full_name: str,
        language_code: str,
        timezone: str,
    ) -> User:
        user = User(
            telegram_id=telegram_id,
            username=username,
            full_name=full_name,
            language_code=language_code,
            timezone=timezone,
        )
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def update_status(self, user: User, status: UserStatus) -> User:
        user.status = status
        await self.session.flush()
        return user

    async def update_language(self, user: User, language_code: str) -> User:
        user.language_code = language_code
        await self.session.flush()
        return user

    async def update_timezone(self, user: User, timezone: str) -> User:
        user.timezone = timezone
        await self.session.flush()
        return user

    async def update_notification_minutes_before(self, user: User, minutes: int) -> User:
        user.notification_minutes_before = minutes
        await self.session.flush()
        return user
