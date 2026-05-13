from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.enums import RoleType
from src.models.role import Role


class RoleRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add_role(self, user_id: int, role_type: RoleType) -> Role:
        role = Role(user_id=user_id, role_type=role_type)
        self.session.add(role)
        await self.session.flush()
        return role

    async def get_user_roles(self, user_id: int) -> list[Role]:
        result = await self.session.execute(
            select(Role).where(Role.user_id == user_id)
        )
        return list(result.scalars().all())

    async def remove_role(self, user_id: int, role_type: RoleType) -> None:
        result = await self.session.execute(
            select(Role).where(Role.user_id == user_id, Role.role_type == role_type)
        )
        role = result.scalar_one_or_none()
        if role:
            await self.session.delete(role)
            await self.session.flush()
