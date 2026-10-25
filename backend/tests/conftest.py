"""Shared test fixtures for the WindWatch test suite."""

from __future__ import annotations

import json
from collections.abc import Iterator
from datetime import datetime, timedelta
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_current_store
from app.domain.models import Store
from app.main import app

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _make_hour(day: str, hour: int) -> datetime:
    return datetime.fromisoformat(f"{day}T{hour:02d}:00:00+00:00")


def build_sample_store() -> Store:
    """Build a deterministic in-memory Store for domain and API contract tests."""
    actuals: dict[datetime, float] = {}
    # Even hours: half-hours 1000 and 3000 MW (hourly mean = 2000 MW)
    # Odd hours: half-hours 3000 and 5000 MW (hourly mean = 4000 MW)
    for hour in range(24):
        start = _make_hour("2026-01-15", hour)
        if hour % 2 == 0:
            actuals[start] = 1000.0
            actuals[start + timedelta(minutes=30)] = 3000.0
        else:
            actuals[start] = 3000.0
            actuals[start + timedelta(minutes=30)] = 5000.0

    def curve(level: float) -> dict[datetime, float]:
        return {_make_hour("2026-01-15", hour): level for hour in range(24)}

    forecasts = {
        _make_hour("2026-01-14", 2).replace(minute=30): curve(3000.0),
        _make_hour("2026-01-14", 4).replace(minute=30): curve(5000.0),
        _make_hour("2026-01-14", 7).replace(minute=30): curve(9000.0),
    }

    # Samples for horizon table verification
    actuals[_make_hour("2026-01-16", 12)] = 4000.0
    actuals[_make_hour("2026-01-16", 12) + timedelta(minutes=30)] = 4000.0
    forecasts[_make_hour("2026-01-16", 10)] = {_make_hour("2026-01-16", 12): 4600.0}
    forecasts[_make_hour("2026-01-15", 6)] = {_make_hour("2026-01-16", 12): 5200.0}

    return Store(actuals=actuals, forecasts=forecasts, fetched_at="test_store")


@pytest.fixture
def sample_store() -> Store:
    """Provide a fresh sample Store instance."""
    return build_sample_store()


@pytest.fixture
def client(sample_store: Store) -> Iterator[TestClient]:
    """TestClient with dependency overrides pre-configured for the sample store."""
    app.dependency_overrides[get_current_store] = lambda: sample_store
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def fuelhh_fixture() -> list[dict]:
    """Load recorded FUELHH JSON response fixture."""
    path = FIXTURES_DIR / "fuelhh_sample.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def windfor_fixture() -> list[dict]:
    """Load recorded WINDFOR JSON response fixture."""
    path = FIXTURES_DIR / "windfor_sample.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)
