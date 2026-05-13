from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_i18n import I18nContext

from src.models.schedule import Schedule


class DurationCallback(CallbackData, prefix="dur"):
    minutes: int


class RecurrenceCallback(CallbackData, prefix="rec"):
    recurrence_type: str


class RecurrenceDayCallback(CallbackData, prefix="rec_day"):
    day: str
    action: str


class ScheduleActionCallback(CallbackData, prefix="sched_action"):
    schedule_id: int
    action: str


DURATION_OPTIONS = [30, 45, 60, 90, 120]


def build_duration_keyboard(i18n: I18nContext) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    labels = {
        30: i18n.get("btn-duration-30"),
        45: i18n.get("btn-duration-45"),
        60: i18n.get("btn-duration-60"),
        90: i18n.get("btn-duration-90"),
        120: i18n.get("btn-duration-120"),
    }
    for minutes in DURATION_OPTIONS:
        builder.button(text=labels[minutes], callback_data=DurationCallback(minutes=minutes))
    builder.adjust(3, 2)
    return builder.as_markup()


def build_recurrence_keyboard(i18n: I18nContext) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    options = [
        ("none", i18n.get("btn-recurrence-none")),
        ("daily", i18n.get("btn-recurrence-daily")),
        ("weekly", i18n.get("btn-recurrence-weekly")),
        ("monthly", i18n.get("btn-recurrence-monthly")),
    ]
    for recurrence_type, label in options:
        builder.button(
            text=label,
            callback_data=RecurrenceCallback(recurrence_type=recurrence_type),
        )
    builder.adjust(2, 2)
    return builder.as_markup()


WEEKDAY_CODES = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"]
WEEKDAY_KEYS = ["day-mon", "day-tue", "day-wed", "day-thu", "day-fri", "day-sat", "day-sun"]


def build_recurrence_days_keyboard(
    selected_days: list[str], i18n: I18nContext
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for code, key in zip(WEEKDAY_CODES, WEEKDAY_KEYS):
        is_selected = code in selected_days
        label = f"{'✅' if is_selected else '☐'} {i18n.get(key)}"
        builder.button(
            text=label,
            callback_data=RecurrenceDayCallback(day=code, action="toggle"),
        )
    builder.button(
        text=i18n.get("btn-done"),
        callback_data=RecurrenceDayCallback(day="", action="done"),
    )
    builder.adjust(4, 3, 1)
    return builder.as_markup()


def build_schedule_confirm_keyboard(i18n: I18nContext) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=i18n.get("btn-confirm"), callback_data="schedule_confirm")
    builder.button(text=i18n.get("btn-cancel"), callback_data="schedule_cancel_creation")
    builder.adjust(2)
    return builder.as_markup()


def build_schedule_list_keyboard(
    schedules: list[Schedule], i18n: I18nContext
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for schedule in schedules:
        builder.button(
            text=i18n.get("btn-view-schedule", title=schedule.title),
            callback_data=ScheduleActionCallback(schedule_id=schedule.id, action="view"),
        )
    builder.adjust(1)
    return builder.as_markup()


def build_schedule_detail_keyboard(
    schedule: Schedule, i18n: I18nContext, is_admin: bool = False
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if is_admin and not schedule.is_cancelled:
        builder.button(
            text=i18n.get("btn-cancel-schedule"),
            callback_data=ScheduleActionCallback(schedule_id=schedule.id, action="cancel"),
        )
    builder.button(
        text=i18n.get("btn-back"),
        callback_data=ScheduleActionCallback(schedule_id=0, action="back"),
    )
    builder.adjust(1)
    return builder.as_markup()
