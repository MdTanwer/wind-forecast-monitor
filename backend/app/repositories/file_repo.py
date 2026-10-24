"""File-based snapshot repository for Store persistence."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from app.domain.models import DEFAULT_SOURCE, Store
from app.integrations.elexon.client import parse_iso

logger = logging.getLogger(__name__)


class FileDataRepository:
    """Saves and loads market data snapshots to/from a local JSON file."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def load_snapshot(self) -> Store | None:
        """Load Store snapshot from JSON file if it exists."""
        if not self.path.exists():
            return None
        try:
            with open(self.path, encoding="utf-8") as f:
                data = json.load(f)

            actuals = {parse_iso(k): float(v) for k, v in data.get("actuals", {}).items()}
            forecasts = {
                parse_iso(pub): {parse_iso(hour): float(val) for hour, val in curve.items()}
                for pub, curve in data.get("forecasts", {}).items()
            }
            store = Store(
                actuals=actuals,
                forecasts=forecasts,
                fetched_at=data.get("fetched_at", ""),
                source=data.get("source", DEFAULT_SOURCE),
            )
        except Exception as exc:
            logger.warning("Failed to load snapshot from %s: %s", self.path, exc)
            return None

        logger.info(
            "Loaded snapshot from %s (%d actuals, %d forecast publications)",
            self.path,
            len(actuals),
            len(forecasts),
        )
        return store

    def save_snapshot(self, store: Store) -> None:
        """Save Store snapshot to JSON file atomically."""
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            temp_path = self.path.with_suffix(".tmp")

            serialized = {
                "fetched_at": store.fetched_at,
                "source": store.source,
                "actuals": {k.isoformat(): v for k, v in store.actuals.items()},
                "forecasts": {
                    pub.isoformat(): {h.isoformat(): v for h, v in curve.items()}
                    for pub, curve in store.forecasts.items()
                },
            }

            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(serialized, f)
            temp_path.replace(self.path)
            logger.info("Saved data snapshot to %s", self.path)
        except Exception as exc:
            logger.warning("Failed to save snapshot to %s: %s", self.path, exc)
