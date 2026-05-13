from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    bot_token: str
    admin_telegram_ids: list[int] = []

    postgres_host: str = "postgres"
    postgres_port: int = 5432
    postgres_db: str = "schedule_bot"
    postgres_user: str = "schedule_bot"
    postgres_password: str = "change_me"

    redis_host: str = "redis"
    redis_port: int = 6379

    default_locale: str = "uk"
    default_timezone: str = "Europe/Kyiv"
    default_notification_minutes_before: int = 60

    event_queue_poll_interval_seconds: float = 10.0
    notification_schedule_days_ahead: int = 90

    @field_validator("admin_telegram_ids", mode="before")
    @classmethod
    def parse_admin_telegram_ids(cls, value: str | list) -> list[int]:
        if isinstance(value, str):
            return [int(x.strip()) for x in value.split(",") if x.strip()]
        return value

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}"


settings = Settings()
