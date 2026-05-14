from typing import Protocol

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_i18n import I18nContext

from src.domain.enums import RoleType
from src.models.user import User


class Translator(Protocol):
    def __call__(self, key: str, **kwargs: str) -> str: ...


class AdminUserApprovalCallback(CallbackData, prefix="admin_approve"):
    action: str
    target_user_id: int


class ParticipantToggleCallback(CallbackData, prefix="part_toggle"):
    user_id: int


class ParticipantDoneCallback(CallbackData, prefix="part_done"):
    pass


def build_user_approval_keyboard(
    target_user_id: int, i18n: Translator,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=i18n("btn-approve-user"),
        callback_data=AdminUserApprovalCallback(action="user", target_user_id=target_user_id),
    )
    builder.button(
        text=i18n("btn-approve-teacher"),
        callback_data=AdminUserApprovalCallback(action="teacher", target_user_id=target_user_id),
    )
    builder.button(
        text=i18n("btn-reject"),
        callback_data=AdminUserApprovalCallback(action="reject", target_user_id=target_user_id),
    )
    builder.adjust(2, 1)
    return builder.as_markup()


def build_participants_keyboard(
    all_users: list[User],
    selected_ids: list[int],
    i18n: I18nContext,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for user in all_users:
        is_selected = user.id in selected_ids
        role_labels = []
        for role in user.roles:
            if role.role_type == RoleType.TEACHER:
                role_labels.append("🎓")
            elif role.role_type == RoleType.ADMIN:
                role_labels.append("👑")
        role_str = " ".join(role_labels) if role_labels else "👤"
        checkmark = "☑️" if is_selected else "☐"
        builder.button(
            text=f"{checkmark} {role_str} {user.full_name}",
            callback_data=ParticipantToggleCallback(user_id=user.id),
        )
    builder.button(
        text=i18n.get("btn-done"),
        callback_data=ParticipantDoneCallback(),
    )
    row_widths = [1] * len(all_users) + [1]
    builder.adjust(*row_widths)
    return builder.as_markup()
