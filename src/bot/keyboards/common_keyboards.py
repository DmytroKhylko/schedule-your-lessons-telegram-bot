from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_i18n import I18nContext

from src.domain.enums import RoleType
from src.models.user import User


def build_admin_main_menu(i18n: I18nContext, pending_count: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=i18n.get("btn-pending-requests", count=str(pending_count)),
        callback_data="menu:pending",
    )
    builder.button(text=i18n.get("btn-schedules"), callback_data="menu:schedules")
    builder.button(text=i18n.get("btn-users"), callback_data="menu:users")
    builder.button(text=i18n.get("btn-settings"), callback_data="menu:settings")
    builder.adjust(2, 2)
    return builder.as_markup()


def build_user_main_menu(i18n: I18nContext) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=i18n.get("btn-my-schedule"), callback_data="menu:my_schedule")
    builder.button(text=i18n.get("btn-settings"), callback_data="menu:settings")
    builder.adjust(1)
    return builder.as_markup()


def build_schedules_admin_menu(i18n: I18nContext) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=i18n.get("btn-create"), callback_data="menu:create_schedule")
    builder.button(text=i18n.get("btn-my-schedule"), callback_data="menu:all_schedules")
    builder.button(text=i18n.get("btn-back"), callback_data="menu:back_to_main")
    builder.adjust(2, 1)
    return builder.as_markup()


def build_settings_keyboard(i18n: I18nContext) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=i18n.get("btn-change-language"), callback_data="settings:language")
    builder.button(text=i18n.get("btn-change-notification"), callback_data="settings:notification")
    builder.button(text=i18n.get("btn-change-timezone"), callback_data="settings:timezone")
    builder.button(text=i18n.get("btn-back"), callback_data="menu:back_to_main")
    builder.adjust(1)
    return builder.as_markup()


def build_language_keyboard(i18n: I18nContext) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=i18n.get("btn-lang-uk"), callback_data="lang:uk")
    builder.button(text=i18n.get("btn-lang-en"), callback_data="lang:en")
    builder.button(text=i18n.get("btn-back"), callback_data="settings:back")
    builder.adjust(2, 1)
    return builder.as_markup()


def build_notification_keyboard(i18n: I18nContext) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=i18n.get("btn-notify-15"), callback_data="notify:15")
    builder.button(text=i18n.get("btn-notify-30"), callback_data="notify:30")
    builder.button(text=i18n.get("btn-notify-60"), callback_data="notify:60")
    builder.button(text=i18n.get("btn-notify-120"), callback_data="notify:120")
    builder.button(text=i18n.get("btn-back"), callback_data="settings:back")
    builder.adjust(2, 2, 1)
    return builder.as_markup()


TIMEZONES = [
    ("Europe/Kyiv", "🇺🇦 Kyiv (UTC+2/+3)"),
    ("Europe/Warsaw", "🇵🇱 Warsaw (UTC+1/+2)"),
    ("Europe/London", "🇬🇧 London (UTC+0/+1)"),
    ("Europe/Berlin", "🇩🇪 Berlin (UTC+1/+2)"),
    ("Europe/Paris", "🇫🇷 Paris (UTC+1/+2)"),
    ("America/New_York", "🇺🇸 New York (UTC-5/-4)"),
    ("America/Los_Angeles", "🇺🇸 Los Angeles (UTC-8/-7)"),
    ("Asia/Dubai", "🇦🇪 Dubai (UTC+4)"),
    ("Asia/Tbilisi", "🇬🇪 Tbilisi (UTC+4)"),
    ("Asia/Tokyo", "🇯🇵 Tokyo (UTC+9)"),
]


def build_timezone_keyboard(i18n: I18nContext) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for tz_id, tz_label in TIMEZONES:
        builder.button(text=tz_label, callback_data=f"tz:{tz_id}")
    builder.button(text=i18n.get("btn-back"), callback_data="settings:back")
    builder.adjust(1)
    return builder.as_markup()


def build_skip_keyboard(i18n: I18nContext) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=i18n.get("btn-skip"), callback_data="skip")
    return builder.as_markup()
