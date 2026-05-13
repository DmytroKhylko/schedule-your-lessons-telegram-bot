from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram_i18n import I18nContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.filters.role_filter import ActiveUserFilter
from src.bot.keyboards.common_keyboards import (
    build_language_keyboard,
    build_notification_keyboard,
    build_settings_keyboard,
    build_timezone_keyboard,
)
from src.domain.enums import RoleType
from src.models.user import User
from src.repositories.role_repository import RoleRepository
from src.repositories.user_repository import UserRepository
from src.services.user_service import UserService

router = Router()
router.callback_query.filter(ActiveUserFilter())


@router.callback_query(lambda c: c.data == "menu:settings")
async def handle_settings_menu(
    callback: CallbackQuery,
    i18n: I18nContext,
    current_user: User,
) -> None:
    language_display = "🇺🇦 Українська" if current_user.language_code == "uk" else "🇬🇧 English"
    await callback.message.edit_text(
        i18n.get(
            "settings-menu",
            language=language_display,
            minutes=str(current_user.notification_minutes_before),
            timezone=current_user.timezone,
        ),
        reply_markup=build_settings_keyboard(i18n),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "settings:back")
async def handle_settings_back(
    callback: CallbackQuery,
    i18n: I18nContext,
    current_user: User,
) -> None:
    language_display = "🇺🇦 Українська" if current_user.language_code == "uk" else "🇬🇧 English"
    await callback.message.edit_text(
        i18n.get(
            "settings-menu",
            language=language_display,
            minutes=str(current_user.notification_minutes_before),
            timezone=current_user.timezone,
        ),
        reply_markup=build_settings_keyboard(i18n),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "settings:language")
async def handle_language_menu(
    callback: CallbackQuery,
    i18n: I18nContext,
) -> None:
    await callback.message.edit_text(
        i18n.get("language-select"),
        reply_markup=build_language_keyboard(i18n),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("lang:"))
async def handle_language_change(
    callback: CallbackQuery,
    i18n: I18nContext,
    db_session: AsyncSession,
    current_user: User,
) -> None:
    locale = callback.data.split(":")[1]
    user_repository = UserRepository(db_session)
    role_repository = RoleRepository(db_session)
    user_service = UserService(user_repository, role_repository)
    await user_service.update_language(current_user, locale)
    await i18n.set_locale(locale)
    await callback.message.edit_text(i18n.get("settings-language-changed"))
    await callback.answer()


@router.callback_query(lambda c: c.data == "settings:notification")
async def handle_notification_menu(
    callback: CallbackQuery,
    i18n: I18nContext,
) -> None:
    await callback.message.edit_text(
        i18n.get("notification-select"),
        reply_markup=build_notification_keyboard(i18n),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("notify:"))
async def handle_notification_change(
    callback: CallbackQuery,
    i18n: I18nContext,
    db_session: AsyncSession,
    current_user: User,
) -> None:
    minutes = int(callback.data.split(":")[1])
    user_repository = UserRepository(db_session)
    role_repository = RoleRepository(db_session)
    user_service = UserService(user_repository, role_repository)
    await user_service.update_notification_minutes_before(current_user, minutes)
    await callback.message.edit_text(
        i18n.get("settings-notification-changed", minutes=str(minutes))
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "settings:timezone")
async def handle_timezone_menu(
    callback: CallbackQuery,
    i18n: I18nContext,
) -> None:
    await callback.message.edit_text(
        i18n.get("timezone-select"),
        reply_markup=build_timezone_keyboard(i18n),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("tz:"))
async def handle_timezone_change(
    callback: CallbackQuery,
    i18n: I18nContext,
    db_session: AsyncSession,
    current_user: User,
) -> None:
    timezone_str = callback.data[3:]
    user_repository = UserRepository(db_session)
    role_repository = RoleRepository(db_session)
    user_service = UserService(user_repository, role_repository)
    await user_service.update_timezone(current_user, timezone_str)
    await callback.message.edit_text(
        i18n.get("settings-timezone-changed", timezone=timezone_str)
    )
    await callback.answer()
