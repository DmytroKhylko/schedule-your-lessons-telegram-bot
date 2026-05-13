from datetime import date, datetime, time
from zoneinfo import ZoneInfo

from aiogram import Bot, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram_i18n import I18nContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.filters.role_filter import AdminFilter
from src.bot.keyboards.admin_keyboards import (
    ParticipantDoneCallback,
    ParticipantToggleCallback,
    build_participants_keyboard,
)
from src.bot.keyboards.calendar_keyboard import CalendarCallback, build_calendar
from src.bot.keyboards.common_keyboards import (
    build_admin_main_menu,
    build_schedules_admin_menu,
    build_skip_keyboard,
)
from src.bot.keyboards.schedule_keyboards import (
    DurationCallback,
    RecurrenceCallback,
    RecurrenceDayCallback,
    WEEKDAY_CODES,
    WEEKDAY_KEYS,
    build_duration_keyboard,
    build_recurrence_keyboard,
    build_recurrence_days_keyboard,
    build_schedule_confirm_keyboard,
)
from src.bot.states.schedule_states import ScheduleCreationStates
from src.models.user import User
from src.repositories.role_repository import RoleRepository
from src.repositories.schedule_assignment_repository import ScheduleAssignmentRepository
from src.repositories.schedule_repository import ScheduleRepository
from src.repositories.user_repository import UserRepository
from src.services.notification_service import NotificationService
from src.services.schedule_service import ScheduleService
from src.services.user_service import UserService

router = Router()
router.message.filter(AdminFilter())
router.callback_query.filter(AdminFilter())


@router.callback_query(lambda c: c.data == "menu:schedules")
async def handle_schedules_menu(
    callback: CallbackQuery,
    i18n: I18nContext,
    current_user: User,
) -> None:
    await callback.message.edit_text(
        i18n.get("main-menu-admin"),
        reply_markup=build_schedules_admin_menu(i18n),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "menu:back_to_main")
async def handle_back_to_main(
    callback: CallbackQuery,
    i18n: I18nContext,
    db_session: AsyncSession,
    current_user: User,
) -> None:
    user_repository = UserRepository(db_session)
    role_repository = RoleRepository(db_session)
    user_service = UserService(user_repository, role_repository)
    pending_users = await user_service.get_pending_users()

    await callback.message.edit_text(
        i18n.get("main-menu-admin"),
        reply_markup=build_admin_main_menu(i18n, len(pending_users)),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "menu:create_schedule")
async def handle_create_schedule_start(
    callback: CallbackQuery,
    i18n: I18nContext,
    state: FSMContext,
) -> None:
    await state.set_state(ScheduleCreationStates.waiting_for_title)
    await callback.message.edit_text(i18n.get("schedule-ask-title"))
    await callback.answer()


@router.message(ScheduleCreationStates.waiting_for_title)
async def handle_schedule_title(
    message: Message,
    i18n: I18nContext,
    state: FSMContext,
    current_user: User,
) -> None:
    await state.update_data(title=message.text)
    await state.set_state(ScheduleCreationStates.waiting_for_date)
    today = date.today()
    await message.answer(
        i18n.get("schedule-ask-date"),
        reply_markup=build_calendar(today.year, today.month, i18n.locale),
    )


@router.callback_query(CalendarCallback.filter(), ScheduleCreationStates.waiting_for_date)
async def handle_calendar_callback(
    callback: CallbackQuery,
    callback_data: CalendarCallback,
    i18n: I18nContext,
    state: FSMContext,
) -> None:
    if callback_data.action == "ignore":
        await callback.answer()
        return

    if callback_data.action in ("prev", "next"):
        await callback.message.edit_reply_markup(
            reply_markup=build_calendar(callback_data.year, callback_data.month, i18n.locale)
        )
        await callback.answer()
        return

    if callback_data.action == "day":
        selected_date = date(callback_data.year, callback_data.month, callback_data.day)
        if selected_date < date.today():
            await callback.answer(i18n.get("error-past-date"), show_alert=True)
            return

        await state.update_data(date=selected_date.isoformat())
        await state.set_state(ScheduleCreationStates.waiting_for_time)
        await callback.message.edit_text(i18n.get("schedule-ask-time"))
        await callback.answer()


@router.message(ScheduleCreationStates.waiting_for_time)
async def handle_schedule_time(
    message: Message,
    i18n: I18nContext,
    state: FSMContext,
) -> None:
    text = (message.text or "").strip()
    try:
        parsed_time = datetime.strptime(text, "%H:%M").time()
    except ValueError:
        await message.answer(i18n.get("error-invalid-time"))
        return

    await state.update_data(time=parsed_time.strftime("%H:%M"))
    await state.set_state(ScheduleCreationStates.waiting_for_duration)
    await message.answer(
        i18n.get("schedule-ask-duration"),
        reply_markup=build_duration_keyboard(i18n),
    )


@router.callback_query(DurationCallback.filter(), ScheduleCreationStates.waiting_for_duration)
async def handle_duration_selection(
    callback: CallbackQuery,
    callback_data: DurationCallback,
    i18n: I18nContext,
    state: FSMContext,
) -> None:
    await state.update_data(duration_minutes=callback_data.minutes)
    await state.set_state(ScheduleCreationStates.waiting_for_subject)
    await callback.message.edit_text(
        i18n.get("schedule-ask-subject"),
        reply_markup=build_skip_keyboard(i18n),
    )
    await callback.answer()


@router.message(ScheduleCreationStates.waiting_for_subject)
async def handle_schedule_subject(
    message: Message,
    i18n: I18nContext,
    state: FSMContext,
) -> None:
    await state.update_data(subject=message.text)
    await state.set_state(ScheduleCreationStates.waiting_for_location)
    await message.answer(
        i18n.get("schedule-ask-location"),
        reply_markup=build_skip_keyboard(i18n),
    )


@router.callback_query(lambda c: c.data == "skip", ScheduleCreationStates.waiting_for_subject)
async def handle_skip_subject(
    callback: CallbackQuery,
    i18n: I18nContext,
    state: FSMContext,
) -> None:
    await state.update_data(subject=None)
    await state.set_state(ScheduleCreationStates.waiting_for_location)
    await callback.message.edit_text(
        i18n.get("schedule-ask-location"),
        reply_markup=build_skip_keyboard(i18n),
    )
    await callback.answer()


@router.message(ScheduleCreationStates.waiting_for_location)
async def handle_schedule_location(
    message: Message,
    i18n: I18nContext,
    state: FSMContext,
) -> None:
    await state.update_data(location=message.text)
    await state.set_state(ScheduleCreationStates.waiting_for_recurrence)
    await message.answer(
        i18n.get("schedule-ask-recurrence"),
        reply_markup=build_recurrence_keyboard(i18n),
    )


@router.callback_query(lambda c: c.data == "skip", ScheduleCreationStates.waiting_for_location)
async def handle_skip_location(
    callback: CallbackQuery,
    i18n: I18nContext,
    state: FSMContext,
) -> None:
    await state.update_data(location=None)
    await state.set_state(ScheduleCreationStates.waiting_for_recurrence)
    await callback.message.edit_text(
        i18n.get("schedule-ask-recurrence"),
        reply_markup=build_recurrence_keyboard(i18n),
    )
    await callback.answer()


@router.callback_query(RecurrenceCallback.filter(), ScheduleCreationStates.waiting_for_recurrence)
async def handle_recurrence_selection(
    callback: CallbackQuery,
    callback_data: RecurrenceCallback,
    i18n: I18nContext,
    state: FSMContext,
    db_session: AsyncSession,
    current_user: User,
) -> None:
    await state.update_data(recurrence_type=callback_data.recurrence_type, recurrence_days=[])

    if callback_data.recurrence_type == "weekly":
        await state.set_state(ScheduleCreationStates.waiting_for_recurrence_days)
        await callback.message.edit_text(
            i18n.get("schedule-ask-recurrence-days"),
            reply_markup=build_recurrence_days_keyboard([], i18n),
        )
        await callback.answer()
        return

    await _proceed_to_participants(callback, i18n, state, db_session, current_user)
    await callback.answer()


@router.callback_query(RecurrenceDayCallback.filter(), ScheduleCreationStates.waiting_for_recurrence_days)
async def handle_recurrence_day_toggle(
    callback: CallbackQuery,
    callback_data: RecurrenceDayCallback,
    i18n: I18nContext,
    state: FSMContext,
    db_session: AsyncSession,
    current_user: User,
) -> None:
    data = await state.get_data()
    selected_days: list[str] = list(data.get("recurrence_days", []))

    if callback_data.action == "toggle":
        if callback_data.day in selected_days:
            selected_days.remove(callback_data.day)
        else:
            selected_days.append(callback_data.day)
        await state.update_data(recurrence_days=selected_days)
        await callback.message.edit_reply_markup(
            reply_markup=build_recurrence_days_keyboard(selected_days, i18n)
        )
        await callback.answer()
        return

    if callback_data.action == "done":
        if not selected_days:
            await callback.answer(i18n.get("error-no-recurrence-days"), show_alert=True)
            return
        await _proceed_to_participants(callback, i18n, state, db_session, current_user)
        await callback.answer()


async def _proceed_to_participants(
    callback: CallbackQuery,
    i18n: I18nContext,
    state: FSMContext,
    db_session: AsyncSession,
    current_user: User,
) -> None:
    user_repository = UserRepository(db_session)
    role_repository = RoleRepository(db_session)
    user_service = UserService(user_repository, role_repository)
    all_users = await user_service.get_all_assignable_users()

    await state.update_data(selected_participant_ids=[], all_user_ids=[u.id for u in all_users])
    await state.set_state(ScheduleCreationStates.waiting_for_participants)
    await callback.message.edit_text(
        i18n.get("schedule-ask-participants"),
        reply_markup=build_participants_keyboard(all_users, [], i18n),
    )


@router.callback_query(ParticipantToggleCallback.filter(), ScheduleCreationStates.waiting_for_participants)
async def handle_participant_toggle(
    callback: CallbackQuery,
    callback_data: ParticipantToggleCallback,
    i18n: I18nContext,
    state: FSMContext,
    db_session: AsyncSession,
    current_user: User,
) -> None:
    data = await state.get_data()
    selected_ids: list[int] = list(data.get("selected_participant_ids", []))

    if callback_data.user_id in selected_ids:
        selected_ids.remove(callback_data.user_id)
    else:
        selected_ids.append(callback_data.user_id)

    await state.update_data(selected_participant_ids=selected_ids)

    user_repository = UserRepository(db_session)
    role_repository = RoleRepository(db_session)
    user_service = UserService(user_repository, role_repository)
    all_users = await user_service.get_all_assignable_users()

    await callback.message.edit_reply_markup(
        reply_markup=build_participants_keyboard(all_users, selected_ids, i18n)
    )
    await callback.answer()


@router.callback_query(ParticipantDoneCallback.filter(), ScheduleCreationStates.waiting_for_participants)
async def handle_participants_done(
    callback: CallbackQuery,
    i18n: I18nContext,
    state: FSMContext,
    current_user: User,
) -> None:
    data = await state.get_data()
    selected_ids: list[int] = data.get("selected_participant_ids", [])

    if not selected_ids:
        await callback.answer(i18n.get("schedule-no-participants"), show_alert=True)
        return

    await state.set_state(ScheduleCreationStates.confirming)
    preview_text = _build_preview_text(data, i18n)
    await callback.message.edit_text(
        preview_text,
        reply_markup=build_schedule_confirm_keyboard(i18n),
    )
    await callback.answer()


def _build_preview_text(data: dict, i18n: I18nContext) -> str:
    subject_line = (
        i18n.get("schedule-confirm-subject-line", subject=data["subject"])
        if data.get("subject")
        else ""
    )
    location_line = (
        i18n.get("schedule-confirm-location-line", location=data["location"])
        if data.get("location")
        else ""
    )
    recurrence_type = data.get("recurrence_type", "none")
    recurrence_days = data.get("recurrence_days", [])
    recurrence_label = _format_recurrence(recurrence_type, recurrence_days, i18n)
    recurrence_line = (
        i18n.get("schedule-confirm-recurrence-line", recurrence=recurrence_label)
        if recurrence_type != "none"
        else ""
    )
    participant_count = len(data.get("selected_participant_ids", []))

    return i18n.get(
        "schedule-confirm-preview",
        title=data["title"],
        subject_line=subject_line,
        location_line=location_line,
        date=data["date"],
        time=data["time"],
        duration=str(data["duration_minutes"]),
        recurrence_line=recurrence_line,
        participant_count=str(participant_count),
    )


def _format_recurrence(recurrence_type: str, days: list[str], i18n: I18nContext) -> str:
    if recurrence_type == "daily":
        return i18n.get("recurrence-daily")
    if recurrence_type == "monthly":
        return i18n.get("recurrence-monthly")
    if recurrence_type == "weekly" and days:
        day_key_map = dict(zip(WEEKDAY_CODES, WEEKDAY_KEYS))
        days_str = ", ".join(i18n.get(day_key_map[d]) for d in days if d in day_key_map)
        return i18n.get("recurrence-weekly-short", days=days_str)
    return ""


def _build_rrule(recurrence_type: str, days: list[str]) -> str | None:
    if recurrence_type == "none":
        return None
    if recurrence_type == "daily":
        return "FREQ=DAILY"
    if recurrence_type == "monthly":
        return "FREQ=MONTHLY"
    if recurrence_type == "weekly" and days:
        return f"FREQ=WEEKLY;BYDAY={','.join(days)}"
    return None


@router.callback_query(lambda c: c.data == "schedule_confirm", ScheduleCreationStates.confirming)
async def handle_schedule_confirm(
    callback: CallbackQuery,
    i18n: I18nContext,
    state: FSMContext,
    db_session: AsyncSession,
    current_user: User,
    bot: Bot,
) -> None:
    data = await state.get_data()
    await state.clear()

    date_str = data["date"]
    time_str = data["time"]
    user_tz = ZoneInfo(current_user.timezone)

    naive_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    starts_at_local = naive_dt.replace(tzinfo=user_tz)
    starts_at_utc = starts_at_local.astimezone(ZoneInfo("UTC"))

    recurrence_rule = _build_rrule(
        data.get("recurrence_type", "none"), data.get("recurrence_days", [])
    )

    schedule_repository = ScheduleRepository(db_session)
    assignment_repository = ScheduleAssignmentRepository(db_session)
    schedule_service = ScheduleService(schedule_repository, assignment_repository)

    schedule = await schedule_service.create_schedule(
        title=data["title"],
        starts_at=starts_at_utc,
        duration_minutes=data["duration_minutes"],
        created_by=current_user,
        subject=data.get("subject"),
        location=data.get("location"),
        recurrence_rule=recurrence_rule,
        participant_ids=data.get("selected_participant_ids", []),
    )

    notification_service = NotificationService(bot)
    assignments = await assignment_repository.get_by_schedule_id(schedule.id)
    for assignment in assignments:
        await notification_service.send_new_assignment_notification(assignment.user, schedule)

    user_repository = UserRepository(db_session)
    role_repository = RoleRepository(db_session)
    user_service = UserService(user_repository, role_repository)
    pending_count = len(await user_service.get_pending_users())

    await callback.message.edit_text(
        i18n.get("schedule-created"),
        reply_markup=build_admin_main_menu(i18n, pending_count),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "schedule_cancel_creation", ScheduleCreationStates.confirming)
async def handle_schedule_cancel_creation(
    callback: CallbackQuery,
    i18n: I18nContext,
    state: FSMContext,
    db_session: AsyncSession,
    current_user: User,
) -> None:
    await state.clear()
    user_repository = UserRepository(db_session)
    role_repository = RoleRepository(db_session)
    user_service = UserService(user_repository, role_repository)
    pending_count = len(await user_service.get_pending_users())

    await callback.message.edit_text(
        i18n.get("schedule-creation-cancelled"),
        reply_markup=build_admin_main_menu(i18n, pending_count),
    )
    await callback.answer()
