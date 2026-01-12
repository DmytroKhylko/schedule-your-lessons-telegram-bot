import os

from dotenv import load_dotenv

load_dotenv()


def require_env(name: str) -> str:
    value = os.getenv(name)
    if value is None:
        raise RuntimeError(f"{name} is not set in .env")
    return value


BOT_TOKEN: str = require_env("BOT_TOKEN")
