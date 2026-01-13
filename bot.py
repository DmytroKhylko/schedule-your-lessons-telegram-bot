import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message

from config import BOT_TOKEN
from logging_config import setup_logging
from middlewares.logging import LoggingMiddleware

setup_logging()
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
dp.message.middleware(LoggingMiddleware())
dp.callback_query.middleware(LoggingMiddleware())


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("Hello, I'm working!")


@dp.errors()
async def on_error(event, exception):
    logger.exception("Unhandled exception: %s", exception)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
