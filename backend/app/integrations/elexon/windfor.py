"""Elexon WINDFOR wind generation forecast stream."""

from __future__ import annotations

import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, date, datetime, time, timedelta

from app.core.config import get_settings
from app.domain.study import DELIVERY_END, DELIVERY_START
from app.integrations.elexon.client import (
    ElexonClient,
    extract_rows,
    parse_iso,
    stamp_utc,
)

# Start querying publications this many days before delivery to catch early day-ahead runs.
LOOKBACK_DAYS = 3
CHUNK_DAYS = 5
MAX_WORKERS = 7


def _utc_midnight(day: date) -> datetime:
    return datetime.combine(day, time.min, tzinfo=UTC)


def fetch_live_windfor_chunk(client: ElexonClient, chunk_start: datetime, chunk_end: datetime) -> list[dict]:
    """Fetch WINDFOR forecasts published within a time window."""
    query = urllib.parse.urlencode(
        {
            "publishDateTimeFrom": stamp_utc(chunk_start),
            "publishDateTimeTo": stamp_utc(chunk_end),
        }
    )
    return extract_rows(client.get_json(f"{get_settings().elexon_windfor_url}?{query}"))


def fetch_forecasts_dynamic(
    delivery_start: date = DELIVERY_START,
    delivery_end: date = DELIVERY_END,
    client: ElexonClient | None = None,
) -> dict[datetime, dict[datetime, float]]:
    """Fetch all WINDFOR vintages for the study window as {publishTime: {hourStart: MW}}."""
    client = client or ElexonClient()

    window_start = _utc_midnight(delivery_start)
    window_end = _utc_midnight(delivery_end + timedelta(days=1))

    chunks: list[tuple[datetime, datetime]] = []
    cursor = window_start - timedelta(days=LOOKBACK_DAYS)
    while cursor < window_end:
        chunk_end = min(cursor + timedelta(days=CHUNK_DAYS), window_end)
        chunks.append((cursor, chunk_end))
        cursor = chunk_end
    if not chunks:
        return {}

    forecasts: dict[datetime, dict[datetime, float]] = {}
    with ThreadPoolExecutor(max_workers=min(len(chunks), MAX_WORKERS)) as executor:
        for rows in executor.map(lambda chunk: fetch_live_windfor_chunk(client, *chunk), chunks):
            for row in rows:
                start_time = row.get("startTime")
                publish_time = row.get("publishTime")
                generation = row.get("generation")
                if not start_time or not publish_time or generation is None:
                    continue

                start = parse_iso(start_time)
                published = parse_iso(publish_time)
                # Keep only delivery-window targets that were published ahead of delivery.
                if not window_start <= start < window_end or published > start:
                    continue

                hour = start.replace(minute=0, second=0, microsecond=0)
                # Rows repeated across chunk boundaries simply overwrite with the same value.
                forecasts.setdefault(published, {})[hour] = float(generation)
    return forecasts
