"""Unit tests for DataService, snapshot persistence, and validation."""

import threading
import time as clock
from pathlib import Path
from unittest.mock import patch

import pytest

from app.core.config import Settings
from app.core.errors import DataValidationError
from app.domain.models import Store
from app.repositories.file_repo import FileDataRepository
from app.services.data_service import DataService


def _service(tmp_path: Path) -> DataService:
    snapshot = tmp_path / "snapshot.json"
    return DataService(settings=Settings(data_dir=tmp_path), repository=FileDataRepository(snapshot))


def test_data_validation_rejects_empty_data():
    with pytest.raises(DataValidationError):
        DataService.validate_data(actuals={}, forecasts={})


def test_file_repository_save_and_load(tmp_path: Path, sample_store: Store):
    snapshot_file = tmp_path / "test_snapshot.json"
    repo = FileDataRepository(snapshot_file)

    repo.save_snapshot(sample_store)
    assert snapshot_file.exists()

    loaded = repo.load_snapshot()
    assert loaded is not None
    assert loaded.actuals == sample_store.actuals
    assert loaded.forecasts == sample_store.forecasts
    assert loaded.fetched_at == sample_store.fetched_at
    assert loaded.source == sample_store.source


def test_data_service_falls_back_to_stale_cache_on_upstream_failure(tmp_path: Path, sample_store: Store):
    service = _service(tmp_path)
    service._cached_store = sample_store

    def failing_fetch(*args, **kwargs):
        raise RuntimeError("Elexon 500 Network Outage")

    with patch("app.services.data_service.fetch_actuals_dynamic", failing_fetch):
        assert service.get_store(force_refresh=True) is sample_store


def test_concurrent_cold_start_fetches_upstream_once(tmp_path: Path, sample_store: Store):
    service = _service(tmp_path)
    calls = 0

    def slow_refresh():
        nonlocal calls
        calls += 1
        clock.sleep(0.05)
        service._cached_store = sample_store
        return sample_store

    with patch.object(service, "refresh", slow_refresh):
        threads = [threading.Thread(target=service.get_store) for _ in range(5)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
    assert calls == 1
