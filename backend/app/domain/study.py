"""Study window for day-ahead purchase decisions made in January 2026.

A decision taken on the morning of day D buys power for delivery on day D+1.
Decisions from 1 January through 31 January therefore cover delivery from
2 January through 1 February 2026.
"""

from __future__ import annotations

from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

LONDON = ZoneInfo("Europe/London")

# First and last delivery dates bought by a January 2026 day-ahead decision.
DELIVERY_START = date(2026, 1, 2)
DELIVERY_END = date(2026, 2, 1)

DEFAULT_DELIVERY_DAY = date(2026, 1, 15)
DEFAULT_DECISION_TIME = time(9, 0)
DEFAULT_HORIZON_HOURS = 4
MAX_HORIZON_HOURS = 36

HORIZON_OPTIONS = (0, 2, 4, 6, 8, 12)

# Lead-time buckets. The upper bound is exclusive.
HORIZON_BUCKETS: tuple[tuple[str, float, float], ...] = (
    ("0–6 h", 0, 6),
    ("6–12 h", 6, 12),
    ("12–24 h", 12, 24),
    ("24–48 h", 24, 48),
)


def delivery_days() -> list[date]:
    days: list[date] = []
    day = DELIVERY_START
    while day <= DELIVERY_END:
        days.append(day)
        day += timedelta(days=1)
    return days


def decision_day(delivery: date) -> date:
    return delivery - timedelta(days=1)


def as_london(day: date, clock: time) -> datetime:
    return datetime.combine(day, clock, tzinfo=LONDON)


def format_day(day: date, *, with_year: bool = False) -> str:
    text = f"{day.day} {day.strftime('%b')}"
    if with_year:
        text = f"{text} {day.year}"
    return text


def format_clock(moment: datetime) -> str:
    local = moment.astimezone(LONDON)
    return f"{local.day} {local.strftime('%b')} {local.strftime('%H:%M')}"
