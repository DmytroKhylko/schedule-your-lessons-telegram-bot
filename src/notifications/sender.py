from datetime import datetime
from zoneinfo import ZoneInfo

from aiogram import Bot
from fluent.runtime import FluentBundle, FluentResource

from src.models.schedule import Schedule
from src.models.user import User

bundles: dict[str, FluentBundle] = {}


def load_bundle(locale: str) -> FluentBundle:
    if locale in bundles:
        return bundles[locale]

    bundle = FluentBundle([locale])
    try:
        with open(f"locales/{locale}/messages.ftl", encoding="utf-8") as f:
            resource = FluentResource(f.read())
        bundle.add_resource(resource)
    except FileNotFoundError:
        with open("locales/en/messages.ftl", encoding="utf-8") as f:
            resource = FluentResource(f.read())
        bundle.add_resource(resource)

    bundles[locale] = bundle
    return bundle


def get_translated_text(locale: str, message_id: str, **kwargs: str) -> str:
    bundle = load_bundle(locale)
    message = bundle.get_message(message_id)
    if not message or not message.value:
        bundle = load_bundle("en")
        message = bundle.get_message(message_id)
    if not message or not message.value:
        return message_id

    value, _ = bundle.format_pattern(message.value, kwargs)
    return value


async def send_lesson_reminder(
    bot: Bot,
    user: User,
    schedule: Schedule,
    occurrence_time: datetime,
) -> None:
    locale = user.language_code
    user_tz = ZoneInfo(user.timezone)
    local_time = occurrence_time.astimezone(user_tz)

    subject = schedule.subject or ""
    location = schedule.location or ""

    subject_line = get_translated_text(locale, "notification-subject-line", subject=subject) if subject else ""
    location_line = get_translated_text(locale, "notification-location-line", location=location) if location else ""

    text = get_translated_text(
        locale,
        "lesson-reminder",
        title=schedule.title,
        subject_line=subject_line,
        date=local_time.strftime("%d.%m.%Y"),
        time=local_time.strftime("%H:%M"),
        duration=str(schedule.duration_minutes),
        location_line=location_line,
        minutes_before=str(user.notification_minutes_before),
    )
    await bot.send_message(user.telegram_id, text)


async def send_new_assignment(
    bot: Bot,
    user: User,
    schedule: Schedule,
) -> None:
    locale = user.language_code
    user_tz = ZoneInfo(user.timezone)
    local_time = schedule.starts_at.astimezone(user_tz)

    subject = schedule.subject or ""
    location = schedule.location or ""

    subject_line = get_translated_text(locale, "notification-subject-line", subject=subject) if subject else ""
    location_line = get_translated_text(locale, "notification-location-line", location=location) if location else ""

    text = get_translated_text(
        locale,
        "new-assignment",
        title=schedule.title,
        subject_line=subject_line,
        date=local_time.strftime("%d.%m.%Y"),
        time=local_time.strftime("%H:%M"),
        duration=str(schedule.duration_minutes),
        location_line=location_line,
    )
    await bot.send_message(user.telegram_id, text)
