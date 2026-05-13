from aiogram import Bot, Router
from aiogram.types import CallbackQuery
from aiogram_i18n import I18nContext
from sqlalchemy.ext.asyncio import AsyncSession

from config import Settings
from src.bot.filters.role_filter import AdminFilter
from src.bot.keyboards.admin_keyboards import AdminUserApprovalCallback, build_user_approval_keyboard
from src.bot.keyboards.common_keyboards import build_admin_main_menu
from src.domain.enums import RoleType
from src.models.user import User
from src.repositories.role_repository import RoleRepository
from src.repositories.user_repository import UserRepository
from src.services.user_service import UserService

router = Router()
router.callback_query.filter(AdminFilter())


@router.callback_query(AdminUserApprovalCallback.filter())
async def handle_user_approval(
    callback: CallbackQuery,
    callback_data: AdminUserApprovalCallback,
    i18n: I18nContext,
    db_session: AsyncSession,
    bot: Bot,
) -> None:
    user_repository = UserRepository(db_session)
    role_repository = RoleRepository(db_session)
    user_service = UserService(user_repository, role_repository)

    target_user = await user_repository.get_by_id(callback_data.target_user_id)
    if not target_user:
        await callback.answer()
        return

    if callback_data.action == "user":
        await user_service.approve(target_user, RoleType.USER)
        await callback.message.edit_text(
            i18n.get("admin-approved-user", full_name=target_user.full_name)
        )
        try:
            await bot.send_message(target_user.telegram_id, i18n.get("user-approved-as-user"))
        except Exception:
            pass

    elif callback_data.action == "teacher":
        await user_service.approve(target_user, RoleType.TEACHER)
        await callback.message.edit_text(
            i18n.get("admin-approved-teacher", full_name=target_user.full_name)
        )
        try:
            await bot.send_message(target_user.telegram_id, i18n.get("user-approved-as-teacher"))
        except Exception:
            pass

    elif callback_data.action == "reject":
        await user_service.reject(target_user)
        await callback.message.edit_text(
            i18n.get("admin-rejected-user", full_name=target_user.full_name)
        )
        try:
            await bot.send_message(target_user.telegram_id, i18n.get("user-rejected"))
        except Exception:
            pass

    await callback.answer()


@router.callback_query(lambda c: c.data == "menu:pending")
async def handle_pending_menu(
    callback: CallbackQuery,
    i18n: I18nContext,
    db_session: AsyncSession,
    settings: Settings,
) -> None:
    user_repository = UserRepository(db_session)
    role_repository = RoleRepository(db_session)
    user_service = UserService(user_repository, role_repository)
    pending_users = await user_service.get_pending_users()

    if not pending_users:
        await callback.message.edit_text(
            i18n.get("no-pending-requests"),
            reply_markup=build_admin_main_menu(i18n, 0),
        )
        await callback.answer()
        return

    for user in pending_users:
        username_display = f"@{user.username}" if user.username else "—"
        await callback.message.answer(
            i18n.get(
                "admin-join-request",
                full_name=user.full_name,
                username=username_display,
            ),
            reply_markup=build_user_approval_keyboard(user.id, i18n),
        )

    await callback.message.edit_text(
        i18n.get("main-menu-admin"),
        reply_markup=build_admin_main_menu(i18n, len(pending_users)),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "menu:users")
async def handle_users_menu(
    callback: CallbackQuery,
    i18n: I18nContext,
    db_session: AsyncSession,
) -> None:
    user_repository = UserRepository(db_session)
    users = await user_repository.get_all_active()

    if not users:
        await callback.message.edit_text(i18n.get("users-list-empty"))
        await callback.answer()
        return

    role_labels = {
        RoleType.ADMIN: i18n.get("role-admin"),
        RoleType.TEACHER: i18n.get("role-teacher"),
        RoleType.USER: i18n.get("role-user"),
    }

    lines = [i18n.get("users-list-header")]
    for user in users:
        roles_str = ", ".join(role_labels[r.role_type] for r in user.roles if r.role_type in role_labels)
        lines.append(i18n.get("user-list-item", full_name=user.full_name, role=roles_str or "—"))

    await callback.message.edit_text("\n".join(lines))
    await callback.answer()
