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

    default_locale: str = "uk"
    default_timezone: str = "Europe/Kyiv"
    default_notification_minutes_before: int = 60

    scheduler_poll_interval_seconds: float = 60.0
    notification_lookahead_hours: int = 24

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


settings = Settings()  # type: ignore[call-arg]
