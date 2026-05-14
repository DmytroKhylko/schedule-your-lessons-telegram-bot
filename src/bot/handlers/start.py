from functools import partial

from aiogram import Bot, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram_i18n import I18nContext
from sqlalchemy.ext.asyncio import AsyncSession

from config import Settings
from src.bot.commands import set_admin_commands, set_user_commands
from src.bot.filters.role_filter import ActiveUserFilter, AdminFilter
from src.bot.keyboards.common_keyboards import build_admin_main_menu, build_user_main_menu
from src.bot.keyboards.admin_keyboards import build_user_approval_keyboard
from src.domain.enums import RoleType, UserStatus
from src.models.user import User
from src.notifications.sender import get_translated_text
from src.repositories.role_repository import RoleRepository
from src.repositories.user_repository import UserRepository
from src.bot.states.schedule_states import ScheduleCreationStates
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

        language = current_user.language_code if current_user else "uk"
        await set_admin_commands(bot, from_user.id, language)

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
                admin_user = await user_repository.get_by_telegram_id(admin_id)
                admin_locale = admin_user.language_code if admin_user else "uk"
                translate = partial(get_translated_text, admin_locale)

                await bot.send_message(
                    admin_id,
                    translate(
                        "admin-join-request",
                        full_name=from_user.full_name,
                        username=username_display,
                    ),
                    reply_markup=build_user_approval_keyboard(new_user.id, translate),
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

        await set_admin_commands(bot, from_user.id, current_user.language_code)
        await message.answer(
            i18n.get("welcome-active", full_name=current_user.full_name),
            reply_markup=build_admin_main_menu(i18n, len(pending_users)),
        )
    else:
        await set_user_commands(bot, from_user.id, current_user.language_code)
        await message.answer(
            i18n.get("welcome-active", full_name=current_user.full_name),
            reply_markup=build_user_main_menu(i18n),
        )


@router.message(Command("help"))
async def handle_help(
    message: Message,
    i18n: I18nContext,
    current_user: User | None,
) -> None:
    is_admin = current_user and any(
        role.role_type == RoleType.ADMIN for role in current_user.roles
    )
    if is_admin:
        await message.answer(i18n.get("help-message-admin"))
    else:
        await message.answer(i18n.get("help-message"))


@router.message(Command("schedule"), ActiveUserFilter())
async def handle_schedule_command(
    message: Message,
    i18n: I18nContext,
    db_session: AsyncSession,
    current_user: User,
) -> None:
    from datetime import datetime, timezone

    from src.bot.keyboards.schedule_keyboards import build_schedule_list_keyboard
    from src.repositories.schedule_assignment_repository import ScheduleAssignmentRepository
    from src.repositories.schedule_repository import ScheduleRepository
    from src.services.schedule_service import ScheduleService

    schedule_repository = ScheduleRepository(db_session)
    assignment_repository = ScheduleAssignmentRepository(db_session)
    schedule_service = ScheduleService(schedule_repository, assignment_repository)

    is_admin = any(role.role_type == RoleType.ADMIN for role in current_user.roles)
    now = datetime.now(tz=timezone.utc)

    if is_admin:
        schedules = await schedule_service.get_upcoming_schedules(now)
    else:
        schedules = await schedule_service.get_upcoming_schedules_for_user(current_user.id, now)

    if not schedules:
        await message.answer(i18n.get("my-schedule-empty"))
        return

    await message.answer(
        i18n.get("my-schedule-header"),
        reply_markup=build_schedule_list_keyboard(schedules, i18n),
    )


@router.message(Command("settings"), ActiveUserFilter())
async def handle_settings_command(
    message: Message,
    i18n: I18nContext,
    current_user: User,
) -> None:
    from src.bot.keyboards.common_keyboards import build_settings_keyboard

    language_display = "🇺🇦 Українська" if current_user.language_code == "uk" else "🇬🇧 English"
    await message.answer(
        i18n.get(
            "settings-menu",
            language=language_display,
            minutes=str(current_user.notification_minutes_before),
            timezone=current_user.timezone,
        ),
        reply_markup=build_settings_keyboard(i18n),
    )


@router.message(Command("create"), AdminFilter())
async def handle_create_command(
    message: Message,
    i18n: I18nContext,
    state: FSMContext,
) -> None:
    await state.set_state(ScheduleCreationStates.waiting_for_title)
    await message.answer(i18n.get("schedule-ask-title"))


@router.message(Command("requests"), AdminFilter())
async def handle_requests_command(
    message: Message,
    i18n: I18nContext,
    db_session: AsyncSession,
    settings: Settings,
) -> None:
    user_repository = UserRepository(db_session)
    role_repository = RoleRepository(db_session)
    user_service = UserService(user_repository, role_repository)
    pending_users = await user_service.get_pending_users()

    if not pending_users:
        await message.answer(i18n.get("no-pending-requests"))
        return

    for user in pending_users:
        username_display = f"@{user.username}" if user.username else "—"
        await message.answer(
            i18n.get(
                "admin-join-request",
                full_name=user.full_name,
                username=username_display,
            ),
            reply_markup=build_user_approval_keyboard(user.id, i18n),
        )


@router.message(Command("users"), AdminFilter())
async def handle_users_command(
    message: Message,
    i18n: I18nContext,
    db_session: AsyncSession,
) -> None:
    user_repository = UserRepository(db_session)
    users = await user_repository.get_all_active()

    if not users:
        await message.answer(i18n.get("users-list-empty"))
        return

    role_labels = {
        RoleType.ADMIN: i18n.get("role-admin"),
        RoleType.TEACHER: i18n.get("role-teacher"),
        RoleType.USER: i18n.get("role-user"),
    }

    lines = [i18n.get("users-list-header")]
    for user in users:
        roles_str = ", ".join(
            role_labels[r.role_type] for r in user.roles if r.role_type in role_labels
        )
        lines.append(i18n.get("user-list-item", full_name=user.full_name, role=roles_str or "—"))

    await message.answer("\n".join(lines))
