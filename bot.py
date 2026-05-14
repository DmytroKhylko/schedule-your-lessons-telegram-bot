import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Update
from aiogram_i18n import I18nMiddleware
from aiogram_i18n.cores import FluentRuntimeCore
from aiogram_i18n.managers import BaseManager
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from config import settings
from logging_config import setup_logging
from middlewares.logging import LoggingMiddleware
from src.bot.commands import set_default_commands
from src.bot.handlers import admin_schedules, admin_users, schedule_view
from src.bot.handlers import settings as settings_handler
from src.bot.handlers import start
from src.bot.middlewares.db_session import DbSessionMiddleware
from src.bot.middlewares.user_context import UserContextMiddleware
from src.models import Base
from src.models.user import User
from src.notifications.scheduler import ReminderScheduler

setup_logging()
logger = logging.getLogger(__name__)


class UserLocaleManager(BaseManager):
    async def get_locale(self, event, current_user: User | None = None, **kwargs) -> str:
        if current_user:
            return current_user.language_code
        from_user = None
        if isinstance(event, Update):
            if event.message:
                from_user = event.message.from_user
            elif event.callback_query:
                from_user = event.callback_query.from_user
            elif event.inline_query:
                from_user = event.inline_query.from_user
        else:
            from_user = getattr(event, "from_user", None)
        if from_user and from_user.language_code:
            return "uk" if from_user.language_code.startswith("uk") else "en"
        return settings.default_locale

    async def set_locale(self, locale: str, **kwargs) -> None:
        pass


async def main() -> None:
    engine = create_async_engine(settings.database_url, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables ensured")

    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    bot = Bot(token=settings.bot_token)

    reminder_scheduler = ReminderScheduler(
        session_factory=session_factory,
        bot=bot,
        poll_interval_seconds=settings.scheduler_poll_interval_seconds,
        lookahead_hours=settings.notification_lookahead_hours,
    )

    dp = Dispatcher(storage=MemoryStorage())
    dp["settings"] = settings

    i18n_middleware = I18nMiddleware(
        core=FluentRuntimeCore(path="locales/{locale}"),
        default_locale=settings.default_locale,
        manager=UserLocaleManager(),
    )

    dp.update.outer_middleware(DbSessionMiddleware(session_factory))
    dp.update.outer_middleware(UserContextMiddleware())
    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())
    i18n_middleware.setup(dp)

    dp.include_router(start.router)
    dp.include_router(admin_users.router)
    dp.include_router(admin_schedules.router)
    dp.include_router(schedule_view.router)
    dp.include_router(settings_handler.router)

    await set_default_commands(bot)
    reminder_scheduler.start()
    logger.info("Bot starting")

    try:
        await dp.start_polling(bot)
    finally:
        await reminder_scheduler.stop()
        await engine.dispose()
        logger.info("Bot stopped")


if __name__ == "__main__":
    asyncio.run(main())
