"""Service for generating and caching day-ahead review summaries."""

from __future__ import annotations

import logging
import threading
from collections import OrderedDict
from datetime import date, datetime, time
from functools import lru_cache

from app.domain.models import Store
from app.domain.review import build_review, horizon_table, hourly_mean_actuals

logger = logging.getLogger(__name__)

# Upper bound on memoised reviews; keys come from user input so the cache must not grow unbounded.
MAX_CACHED_REVIEWS = 512

ReviewKey = tuple[date, time, int]


class ReviewService:
    """Precomputes dataset-level aggregates and memoises review results per dataset."""

    def __init__(self, max_entries: int = MAX_CACHED_REVIEWS) -> None:
        self._lock = threading.Lock()
        self._max_entries = max_entries
        self._store: Store | None = None
        self._hourly_actuals: dict[datetime, float] = {}
        self._horizons: list[dict] = []
        self._reviews: OrderedDict[ReviewKey, dict] = OrderedDict()

    def _sync_store(self, store: Store) -> None:
        """Recompute dataset-level aggregates when a new store is supplied. Caller holds the lock."""
        if self._store is store:
            return
        self._hourly_actuals = hourly_mean_actuals(store.actuals)
        self._horizons = horizon_table(store, self._hourly_actuals)
        self._reviews.clear()
        self._store = store
        logger.debug("Precomputed review aggregates for data version %s", store.fetched_at)

    def get_review(self, store: Store, delivery: date, decision_clock: time, horizon_hours: int) -> dict:
        """Return the day-ahead review, using memoised results where possible."""
        key = (delivery, decision_clock, horizon_hours)
        with self._lock:
            self._sync_store(store)
            cached = self._reviews.get(key)
            if cached is not None:
                self._reviews.move_to_end(key)
                return cached
            hourly_actuals, horizons = self._hourly_actuals, self._horizons

        result = build_review(
            store=store,
            delivery=delivery,
            decision_clock=decision_clock,
            horizon_hours=horizon_hours,
            hourly_actual=hourly_actuals,
            horizons=horizons,
        )

        with self._lock:
            if self._store is store:
                self._reviews[key] = result
                if len(self._reviews) > self._max_entries:
                    self._reviews.popitem(last=False)
        return result


@lru_cache
def get_review_service() -> ReviewService:
    """Process-wide ReviewService instance."""
    return ReviewService()
