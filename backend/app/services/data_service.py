"""Service managing data fetching, caching, background refresh, and validation."""

from __future__ import annotations

import logging
import threading
import time
from datetime import UTC, datetime
from functools import lru_cache

from app.core.config import Settings, get_settings
from app.core.errors import DataValidationError, UpstreamServiceError
from app.domain.models import Store
from app.integrations.elexon.fuelhh import fetch_actuals_dynamic
from app.integrations.elexon.windfor import fetch_forecasts_dynamic
from app.repositories.base import DataRepository
from app.repositories.file_repo import FileDataRepository

logger = logging.getLogger(__name__)

# Minimum data sanity thresholds for the January 2026 delivery window.
MIN_ACTUALS_COUNT = 1000
MIN_FORECASTS_COUNT = 50


class DataService:
    """Thread-safe market data cache with stale-while-revalidate and disk snapshot fallback."""

    def __init__(
        self,
        settings: Settings | None = None,
        repository: DataRepository | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.repository = repository or FileDataRepository(self.settings.snapshot_path)
        # Guards the cache fields and the refreshing flag.
        self._lock = threading.Lock()
        # Serialises upstream fetches so concurrent callers never trigger duplicate downloads.
        self._refresh_lock = threading.Lock()
        self._cached_store: Store | None = None
        self._last_fetched: float = 0.0
        self._is_refreshing = False

        snapshot = self.repository.load_snapshot()
        if snapshot is not None:
            self._cached_store = snapshot
            self._last_fetched = time.time()
            logger.info("Initialized DataService with persisted snapshot.")

    @property
    def cached_store(self) -> Store | None:
        """Return the current cached store in memory, if any."""
        return self._cached_store

    def is_ready(self) -> bool:
        """Return True if market data is available in memory."""
        return self._cached_store is not None

    def is_cache_valid(self) -> bool:
        """Return True if the in-memory cache is still fresh according to TTL."""
        return (
            self._cached_store is not None
            and (time.time() - self._last_fetched) < self.settings.cache_ttl_seconds
        )

    @staticmethod
    def validate_data(actuals: dict, forecasts: dict) -> None:
        """Validate that incoming Elexon data satisfies domain integrity."""
        if len(actuals) < MIN_ACTUALS_COUNT:
            raise DataValidationError(
                f"Actuals count ({len(actuals)}) below minimum required threshold ({MIN_ACTUALS_COUNT})"
            )
        if len(forecasts) < MIN_FORECASTS_COUNT:
            raise DataValidationError(
                f"Forecast publications ({len(forecasts)}) below minimum required threshold ({MIN_FORECASTS_COUNT})"
            )

    def refresh(self) -> Store:
        """Fetch fresh data from Elexon, validate, and update cache and disk.

        Falls back to the stale cache if the fetch fails and a cache exists.
        """
        logger.info("Initiating dynamic fetch from Elexon BMRS API...")
        try:
            actuals = fetch_actuals_dynamic(self.settings.delivery_start, self.settings.delivery_end)
            forecasts = fetch_forecasts_dynamic(self.settings.delivery_start, self.settings.delivery_end)
            self.validate_data(actuals, forecasts)
        except Exception as exc:
            logger.error("Data refresh from Elexon failed: %s", exc)
            if self._cached_store is not None:
                logger.warning("Serving stale cached data due to refresh failure.")
                return self._cached_store
            raise UpstreamServiceError(f"Failed to fetch market data from Elexon: {exc}") from exc

        fetched_at = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        store = Store(actuals=actuals, forecasts=forecasts, fetched_at=fetched_at)
        with self._lock:
            self._cached_store = store
            self._last_fetched = time.time()

        self.repository.save_snapshot(store)
        logger.info(
            "DataService refresh complete: %d actuals, %d forecast runs",
            len(actuals),
            len(forecasts),
        )
        return store

    def get_store(self, force_refresh: bool = False) -> Store:
        """Return the current store, refreshing in the background when stale."""
        cached = self._cached_store
        if cached is not None and not force_refresh:
            if not self.is_cache_valid():
                self._start_background_refresh()
            return cached

        with self._refresh_lock:
            # Another caller may have populated the cache while we waited.
            if not force_refresh and self._cached_store is not None:
                return self._cached_store
            return self.refresh()

    def warm_up(self) -> None:
        """Populate the cache, logging instead of raising on failure (for background use)."""
        try:
            self.get_store()
        except UpstreamServiceError as exc:
            logger.warning("Startup warmup failed; will retry on first request: %s", exc)

    def _start_background_refresh(self) -> None:
        with self._lock:
            if self._is_refreshing:
                return
            self._is_refreshing = True
        threading.Thread(target=self._background_refresh, daemon=True).start()

    def _background_refresh(self) -> None:
        try:
            with self._refresh_lock:
                # refresh() never raises while a cached store exists.
                self.refresh()
        finally:
            with self._lock:
                self._is_refreshing = False


@lru_cache
def get_data_service() -> DataService:
    """Process-wide DataService instance (lazily created on first use)."""
    return DataService()
