from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeChat, BotCommandScopeDefault


USER_COMMANDS = {
    "uk": [
        BotCommand(command="start", description="Головне меню"),
        BotCommand(command="schedule", description="Мій розклад"),
        BotCommand(command="settings", description="Налаштування"),
        BotCommand(command="help", description="Допомога"),
    ],
    "en": [
        BotCommand(command="start", description="Main menu"),
        BotCommand(command="schedule", description="My schedule"),
        BotCommand(command="settings", description="Settings"),
        BotCommand(command="help", description="Help"),
    ],
}

ADMIN_COMMANDS = {
    "uk": [
        BotCommand(command="start", description="Головне меню"),
        BotCommand(command="schedule", description="Мій розклад"),
        BotCommand(command="create", description="Створити розклад"),
        BotCommand(command="requests", description="Запити на приєднання"),
        BotCommand(command="users", description="Список користувачів"),
        BotCommand(command="settings", description="Налаштування"),
        BotCommand(command="help", description="Допомога"),
    ],
    "en": [
        BotCommand(command="start", description="Main menu"),
        BotCommand(command="schedule", description="My schedule"),
        BotCommand(command="create", description="Create schedule"),
        BotCommand(command="requests", description="Join requests"),
        BotCommand(command="users", description="Users list"),
        BotCommand(command="settings", description="Settings"),
        BotCommand(command="help", description="Help"),
    ],
}


async def set_default_commands(bot: Bot) -> None:
    await bot.set_my_commands(USER_COMMANDS["uk"], scope=BotCommandScopeDefault())
    await bot.set_my_commands(
        USER_COMMANDS["en"],
        scope=BotCommandScopeDefault(),
        language_code="en",
    )


async def set_admin_commands(bot: Bot, chat_id: int, language_code: str = "uk") -> None:
    commands = ADMIN_COMMANDS.get(language_code, ADMIN_COMMANDS["en"])
    await bot.set_my_commands(commands, scope=BotCommandScopeChat(chat_id=chat_id))


async def set_user_commands(bot: Bot, chat_id: int, language_code: str = "uk") -> None:
    commands = USER_COMMANDS.get(language_code, USER_COMMANDS["en"])
    await bot.set_my_commands(commands, scope=BotCommandScopeChat(chat_id=chat_id))
