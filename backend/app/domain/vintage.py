"""Forecast vintage selection logic."""

from __future__ import annotations

from datetime import datetime

from app.domain.models import Store


def select_vintage(store: Store, cutoff: datetime) -> tuple[datetime | None, dict[datetime, float]]:
    """Select the latest forecast vintage published at or before the cutoff time."""
    published = store.latest_publication(cutoff)
    if published is None:
        return None, {}
    return published, store.forecasts[published]
