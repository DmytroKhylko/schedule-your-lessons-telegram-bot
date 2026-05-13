from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram_i18n import I18nContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.filters.role_filter import ActiveUserFilter, AdminFilter
from src.bot.keyboards.common_keyboards import build_admin_main_menu, build_user_main_menu
from src.bot.keyboards.schedule_keyboards import (
    ScheduleActionCallback,
    build_schedule_detail_keyboard,
    build_schedule_list_keyboard,
)
from src.domain.enums import RoleType
from src.models.schedule import Schedule
from src.models.user import User
from src.repositories.role_repository import RoleRepository
from src.repositories.schedule_assignment_repository import ScheduleAssignmentRepository
from src.repositories.schedule_repository import ScheduleRepository
from src.repositories.user_repository import UserRepository
from src.services.schedule_service import ScheduleService
from src.services.user_service import UserService

router = Router()
router.callback_query.filter(ActiveUserFilter())

UTC = timezone.utc


@router.callback_query(lambda c: c.data in ("menu:my_schedule", "menu:all_schedules"))
async def handle_my_schedule(
    callback: CallbackQuery,
    i18n: I18nContext,
    db_session: AsyncSession,
    current_user: User,
) -> None:
    schedule_repository = ScheduleRepository(db_session)
    assignment_repository = ScheduleAssignmentRepository(db_session)
    schedule_service = ScheduleService(schedule_repository, assignment_repository)

    is_admin = any(role.role_type == RoleType.ADMIN for role in current_user.roles)
    now = datetime.now(tz=UTC)

    if is_admin and callback.data == "menu:all_schedules":
        schedules = await schedule_service.get_upcoming_schedules(now)
    else:
        schedules = await schedule_service.get_upcoming_schedules_for_user(current_user.id, now)

    if not schedules:
        await callback.message.edit_text(i18n.get("my-schedule-empty"))
        await callback.answer()
        return

    await callback.message.edit_text(
        i18n.get("my-schedule-header"),
        reply_markup=build_schedule_list_keyboard(schedules, i18n),
    )
    await callback.answer()


@router.callback_query(ScheduleActionCallback.filter())
async def handle_schedule_action(
    callback: CallbackQuery,
    callback_data: ScheduleActionCallback,
    i18n: I18nContext,
    db_session: AsyncSession,
    current_user: User,
) -> None:
    if callback_data.action == "back":
        is_admin = any(role.role_type == RoleType.ADMIN for role in current_user.roles)
        if is_admin:
            user_repository = UserRepository(db_session)
            role_repository = RoleRepository(db_session)
            user_service = UserService(user_repository, role_repository)
            pending_count = len(await user_service.get_pending_users())
            await callback.message.edit_text(
                i18n.get("main-menu-admin"),
                reply_markup=build_admin_main_menu(i18n, pending_count),
            )
        else:
            await callback.message.edit_text(
                i18n.get("main-menu-user"),
                reply_markup=build_user_main_menu(i18n),
            )
        await callback.answer()
        return

    schedule_repository = ScheduleRepository(db_session)
    assignment_repository = ScheduleAssignmentRepository(db_session)
    schedule_service = ScheduleService(schedule_repository, assignment_repository)
    schedule = await schedule_service.get_schedule(callback_data.schedule_id)

    if not schedule:
        await callback.answer(i18n.get("schedule-not-found"), show_alert=True)
        return

    is_admin = any(role.role_type == RoleType.ADMIN for role in current_user.roles)

    if callback_data.action == "view":
        text = _format_schedule_detail(schedule, current_user.timezone, i18n)
        await callback.message.edit_text(
            text,
            reply_markup=build_schedule_detail_keyboard(schedule, i18n, is_admin),
        )
        await callback.answer()
        return

    if callback_data.action == "cancel" and is_admin:
        await schedule_service.cancel_schedule(schedule)

        user_repository = UserRepository(db_session)
        role_repository = RoleRepository(db_session)
        user_service = UserService(user_repository, role_repository)
        pending_count = len(await user_service.get_pending_users())

        await callback.message.edit_text(
            i18n.get("schedule-cancelled"),
            reply_markup=build_admin_main_menu(i18n, pending_count),
        )
        await callback.answer()


def _format_schedule_detail(schedule: Schedule, user_timezone: str, i18n: I18nContext) -> str:
    local_dt = schedule.starts_at.astimezone(ZoneInfo(user_timezone))
    date_str = local_dt.strftime("%d.%m.%Y")
    time_str = local_dt.strftime("%H:%M")

    subject_str = (
        i18n.get("schedule-item-subject", subject=schedule.subject) if schedule.subject else ""
    )
    location_str = (
        i18n.get("schedule-item-location", location=schedule.location) if schedule.location else ""
    )

    recurrence_str = ""
    if schedule.recurrence_rule:
        recurrence_label = _parse_recurrence_label(schedule.recurrence_rule, i18n)
        recurrence_str = i18n.get("schedule-item-recurrence", recurrence=recurrence_label)

    return i18n.get(
        "schedule-item",
        title=schedule.title,
        date=date_str,
        time=time_str,
        duration=str(schedule.duration_minutes),
        subject_str=subject_str,
        location_str=location_str,
        recurrence_str=recurrence_str,
    )


def _parse_recurrence_label(rule: str, i18n: I18nContext) -> str:
    if rule == "FREQ=DAILY":
        return i18n.get("recurrence-daily")
    if rule == "FREQ=MONTHLY":
        return i18n.get("recurrence-monthly")
    if rule.startswith("FREQ=WEEKLY"):
        parts = dict(p.split("=") for p in rule.split(";") if "=" in p)
        days = parts.get("BYDAY", "")
        return i18n.get("recurrence-weekly-short", days=days)
    return rule
