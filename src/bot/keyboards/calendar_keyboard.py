import calendar
from datetime import date

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

MONTH_NAMES_UK = [
    "", "Січень", "Лютий", "Березень", "Квітень", "Травень", "Червень",
    "Липень", "Серпень", "Вересень", "Жовтень", "Листопад", "Грудень",
]
MONTH_NAMES_EN = [
    "", "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]
DAY_HEADERS_UK = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Нд"]
DAY_HEADERS_EN = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]


class CalendarCallback(CallbackData, prefix="cal"):
    action: str
    year: int
    month: int
    day: int = 0


def build_calendar(year: int, month: int, locale: str = "uk") -> InlineKeyboardMarkup:
    month_names = MONTH_NAMES_UK if locale == "uk" else MONTH_NAMES_EN
    day_headers = DAY_HEADERS_UK if locale == "uk" else DAY_HEADERS_EN

    builder = InlineKeyboardBuilder()

    prev_year, prev_month = (year, month - 1) if month > 1 else (year - 1, 12)
    next_year, next_month = (year, month + 1) if month < 12 else (year + 1, 1)

    builder.button(
        text="◀",
        callback_data=CalendarCallback(action="prev", year=prev_year, month=prev_month),
    )
    builder.button(
        text=f"{month_names[month]} {year}",
        callback_data=CalendarCallback(action="ignore", year=year, month=month),
    )
    builder.button(
        text="▶",
        callback_data=CalendarCallback(action="next", year=next_year, month=next_month),
    )

    for day_header in day_headers:
        builder.button(
            text=day_header,
            callback_data=CalendarCallback(action="ignore", year=year, month=month),
        )

    today = date.today()
    month_weeks = calendar.monthcalendar(year, month)
    for week in month_weeks:
        for day in week:
            if day == 0:
                builder.button(
                    text=" ",
                    callback_data=CalendarCallback(action="ignore", year=year, month=month),
                )
            else:
                is_past = date(year, month, day) < today
                builder.button(
                    text=f"·{day}·" if is_past else str(day),
                    callback_data=CalendarCallback(
                        action="ignore" if is_past else "day",
                        year=year,
                        month=month,
                        day=day,
                    ),
                )

    rows = [3, 7] + [7] * len(month_weeks)
    builder.adjust(*rows)
    return builder.as_markup()
