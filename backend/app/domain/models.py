"""Domain models representing power generation and forecast datasets."""

from __future__ import annotations

import bisect
from dataclasses import dataclass, field
from datetime import datetime

DEFAULT_SOURCE = "Elexon BMRS Live Streaming API (FUELHH & WINDFOR)"


@dataclass(frozen=True)
class Store:
    """Half-hourly actuals and hourly forecast vintages, keyed by timezone-aware UTC."""

    actuals: dict[datetime, float]
    forecasts: dict[datetime, dict[datetime, float]]
    fetched_at: str
    source: str = DEFAULT_SOURCE
    _publish_times: list[datetime] = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "_publish_times", sorted(self.forecasts))

    def latest_publication(self, cutoff: datetime) -> datetime | None:
        """Binary-search the latest forecast publication at or before `cutoff`."""
        idx = bisect.bisect_right(self._publish_times, cutoff)
        return self._publish_times[idx - 1] if idx else None

    def publications_before(self, cutoff: datetime) -> list[datetime]:
        """Binary-search and return all publication times at or before `cutoff` in chronological order."""
        idx = bisect.bisect_right(self._publish_times, cutoff)
        return self._publish_times[:idx]

    @property
    def peak_actual_mw(self) -> float:
        """Peak wind generation observed in Elexon FUELHH actuals (MW)."""
        return max(self.actuals.values()) if self.actuals else 0.0

    @property
    def peak_actual_gw(self) -> float:
        """Peak wind generation observed in Elexon FUELHH actuals (GW)."""
        return round(self.peak_actual_mw / 1000.0, 2)
