from aiogram import Bot, Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram_i18n import I18nContext
from sqlalchemy.ext.asyncio import AsyncSession

from config import Settings
from src.bot.filters.role_filter import AdminFilter
from src.bot.keyboards.common_keyboards import build_admin_main_menu, build_user_main_menu
from src.bot.keyboards.admin_keyboards import build_user_approval_keyboard
from src.domain.enums import RoleType, UserStatus
from src.models.user import User
from src.repositories.role_repository import RoleRepository
from src.repositories.user_repository import UserRepository
from src.services.user_service import UserService

router = Router()


@router.message(CommandStart())
async def handle_start(
    message: Message,
    i18n: I18nContext,
    current_user: User | None,
    db_session: AsyncSession,
    settings: Settings,
    bot: Bot,
) -> None:
    from_user = message.from_user
    if not from_user:
        return

    if from_user.id in settings.admin_telegram_ids:
        user_repository = UserRepository(db_session)
        role_repository = RoleRepository(db_session)
        user_service = UserService(user_repository, role_repository)
        pending_users = await user_service.get_pending_users()

        await message.answer(
            i18n.get("welcome-admin", full_name=from_user.full_name),
            reply_markup=build_admin_main_menu(i18n, len(pending_users)),
        )
        return

    if current_user is None:
        tg_lang = from_user.language_code or ""
        locale = "uk" if tg_lang.startswith("uk") else "en"

        user_repository = UserRepository(db_session)
        role_repository = RoleRepository(db_session)
        user_service = UserService(user_repository, role_repository)

        new_user, _ = await user_service.register_or_get(
            telegram_id=from_user.id,
            username=from_user.username,
            full_name=from_user.full_name,
            language_code=locale,
            timezone=settings.default_timezone,
        )

        await message.answer(i18n.get("welcome-new", full_name=from_user.full_name))

        username_display = f"@{from_user.username}" if from_user.username else "—"
        for admin_id in settings.admin_telegram_ids:
            try:
                await bot.send_message(
                    admin_id,
                    i18n.get(
                        "admin-join-request",
                        full_name=from_user.full_name,
                        username=username_display,
                    ),
                    reply_markup=build_user_approval_keyboard(new_user.id, i18n),
                )
            except Exception:
                pass
        return

    if current_user.status == UserStatus.PENDING:
        await message.answer(i18n.get("welcome-pending"))
        return

    if current_user.status == UserStatus.REJECTED:
        await message.answer(i18n.get("welcome-rejected"))
        return

    is_admin = any(role.role_type == RoleType.ADMIN for role in current_user.roles)

    if is_admin:
        user_repository = UserRepository(db_session)
        role_repository = RoleRepository(db_session)
        user_service = UserService(user_repository, role_repository)
        pending_users = await user_service.get_pending_users()

        await message.answer(
            i18n.get("welcome-active", full_name=current_user.full_name),
            reply_markup=build_admin_main_menu(i18n, len(pending_users)),
        )
    else:
        await message.answer(
            i18n.get("welcome-active", full_name=current_user.full_name),
            reply_markup=build_user_main_menu(i18n),
        )
