"""Unit tests for FUELHH actuals stream fetching and parsing."""

from datetime import UTC, date, datetime
from unittest.mock import MagicMock

from app.integrations.elexon.fuelhh import fetch_actuals_dynamic, fetch_live_fuelhh_chunk


def test_fetch_live_fuelhh_chunk_filters_rows(fuelhh_fixture: list[dict]):
    mock_client = MagicMock()
    mock_client.get_json.return_value = fuelhh_fixture

    rows = fetch_live_fuelhh_chunk(mock_client, date(2026, 1, 15), date(2026, 1, 15))
    assert len(rows) == 4


def test_fetch_actuals_dynamic_filters_wind_and_keys_by_time(fuelhh_fixture: list[dict]):
    mock_client = MagicMock()
    mock_client.get_json.return_value = fuelhh_fixture

    actuals = fetch_actuals_dynamic(
        start=date(2026, 1, 15),
        end=date(2026, 1, 15),
        client=mock_client,
    )

    # Fixture contains 2 WIND entries and 2 non-WIND entries (CCGT, NUCLEAR)
    assert len(actuals) == 2
    t0 = datetime(2026, 1, 15, 0, 0, tzinfo=UTC)
    t1 = datetime(2026, 1, 15, 0, 30, tzinfo=UTC)
    assert actuals[t0] == 1420.5
    assert actuals[t1] == 1480.0
