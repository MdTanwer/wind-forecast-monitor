"""Elexon FUELHH wind generation actuals stream."""

from __future__ import annotations

import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta

from app.core.config import get_settings
from app.domain.study import DELIVERY_END, DELIVERY_START
from app.integrations.elexon.client import ElexonClient, extract_rows, parse_iso

CHUNK_DAYS = 7
MAX_WORKERS = 6


def fetch_live_fuelhh_chunk(client: ElexonClient, chunk_start: date, chunk_end: date) -> list[dict]:
    """Fetch FUELHH wind actuals for an inclusive settlement-date range."""
    query = urllib.parse.urlencode(
        {
            "settlementDateFrom": chunk_start.isoformat(),
            "settlementDateTo": chunk_end.isoformat(),
            "fuelType": "WIND",
        }
    )
    return extract_rows(client.get_json(f"{get_settings().elexon_fuelhh_url}?{query}"))


def fetch_actuals_dynamic(
    start: date = DELIVERY_START,
    end: date = DELIVERY_END,
    client: ElexonClient | None = None,
) -> dict[datetime, float]:
    """Fetch all FUELHH wind actuals for the delivery window, keyed by UTC start time."""
    client = client or ElexonClient()

    chunks: list[tuple[date, date]] = []
    day = start
    while day <= end:
        chunk_end = min(day + timedelta(days=CHUNK_DAYS - 1), end)
        chunks.append((day, chunk_end))
        day = chunk_end + timedelta(days=1)
    if not chunks:
        return {}

    actuals: dict[datetime, float] = {}
    with ThreadPoolExecutor(max_workers=min(len(chunks), MAX_WORKERS)) as executor:
        for rows in executor.map(lambda chunk: fetch_live_fuelhh_chunk(client, *chunk), chunks):
            for row in rows:
                generation = row.get("generation")
                start_time = row.get("startTime")
                if row.get("fuelType") == "WIND" and generation is not None and start_time:
                    actuals[parse_iso(start_time)] = float(generation)
    return actuals
