"""Abstract repository interface for market data storage and persistence."""

from __future__ import annotations

from typing import Protocol

from app.domain.models import Store


class DataRepository(Protocol):
    """Interface for persisting and loading market data snapshots."""

    def load_snapshot(self) -> Store | None:
        """Load snapshot from persistent storage if available."""
        ...

    def save_snapshot(self, store: Store) -> None:
        """Save store snapshot to persistent storage."""
        ...
