"""Unit tests for WINDFOR forecast stream fetching and vintage mapping."""

from datetime import UTC, date, datetime
from unittest.mock import MagicMock

from app.integrations.elexon.windfor import fetch_forecasts_dynamic, fetch_live_windfor_chunk


def test_fetch_live_windfor_chunk(windfor_fixture: list[dict]):
    mock_client = MagicMock()
    mock_client.get_json.return_value = windfor_fixture

    rows = fetch_live_windfor_chunk(
        mock_client,
        datetime(2026, 1, 14, 0, 0, tzinfo=UTC),
        datetime(2026, 1, 15, 0, 0, tzinfo=UTC),
    )
    assert len(rows) == 4


def test_fetch_forecasts_dynamic_filters_out_of_window_and_published_after(windfor_fixture: list[dict]):
    mock_client = MagicMock()
    mock_client.get_json.return_value = windfor_fixture

    # Test delivery window covering Jan 15
    forecasts = fetch_forecasts_dynamic(
        delivery_start=date(2026, 1, 15),
        delivery_end=date(2026, 1, 15),
        client=mock_client,
    )

    # In fixture:
    # 1. pub 2026-01-14T04:30:00Z -> 2026-01-15T00:00:00Z (valid)
    # 2. pub 2026-01-14T04:30:00Z -> 2026-01-15T01:00:00Z (valid)
    # 3. pub 2026-01-14T07:30:00Z -> 2026-01-15T00:00:00Z (valid)
    # 4. pub 2026-01-15T12:00:00Z -> 2026-01-15T10:00:00Z (published after start time -> excluded)
    pub_0430 = datetime(2026, 1, 14, 4, 30, tzinfo=UTC)
    pub_0730 = datetime(2026, 1, 14, 7, 30, tzinfo=UTC)

    assert pub_0430 in forecasts
    assert pub_0730 in forecasts
    assert len(forecasts[pub_0430]) == 2
    assert forecasts[pub_0430][datetime(2026, 1, 15, 0, 0, tzinfo=UTC)] == 5120.0
