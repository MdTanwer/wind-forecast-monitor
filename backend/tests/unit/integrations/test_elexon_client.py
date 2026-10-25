"""Unit tests for the Elexon BMRS API HTTP client."""

import urllib.error
from datetime import UTC
from unittest.mock import MagicMock, patch

import pytest

from app.core.errors import UpstreamServiceError
from app.integrations.elexon.client import (
    ElexonClient,
    extract_rows,
    parse_iso,
    stamp_utc,
)


def test_parse_iso_and_stamp_utc():
    moment = parse_iso("2026-01-15T09:00:00Z")
    assert moment.tzinfo == UTC
    assert moment.year == 2026
    assert moment.month == 1
    assert moment.day == 15
    assert moment.hour == 9

    stamp = stamp_utc(moment)
    assert stamp == "2026-01-15T09:00:00Z"


def test_extract_rows_from_list_and_dict():
    # Direct list
    raw_list = [{"id": 1}, {"id": 2}]
    assert extract_rows(raw_list) == raw_list

    # Wrapped in data object
    wrapped = {"data": [{"id": 3}]}
    assert extract_rows(wrapped) == [{"id": 3}]

    # Malformed / empty
    assert extract_rows({}) == []
    assert extract_rows({"data": "not a list"}) == []


def test_elexon_client_success():
    client = ElexonClient(max_retries=2, timeout=5)
    mock_resp = MagicMock()
    mock_resp.read.return_value = b'{"data": [{"test": 123}]}'
    mock_resp.__enter__.return_value = mock_resp

    with patch("urllib.request.urlopen", return_value=mock_resp):
        data = client.get_json("https://example.com/stream")
        assert data == {"data": [{"test": 123}]}


def test_elexon_client_non_retryable_4xx():
    client = ElexonClient(max_retries=3, timeout=5)
    err = urllib.error.HTTPError("https://example.com", 404, "Not Found", {}, None)

    with patch("urllib.request.urlopen", side_effect=err), pytest.raises(UpstreamServiceError, match="Elexon HTTP 404"):
        client.get_json("https://example.com")


def test_elexon_client_exhausts_retries_and_raises():
    client = ElexonClient(max_retries=2, timeout=1)
    err = urllib.error.HTTPError("https://example.com", 500, "Server Error", {}, None)

    with (
        patch("urllib.request.urlopen", side_effect=err),
        patch("time.sleep"),
        pytest.raises(UpstreamServiceError, match="failed after 2 attempts"),
    ):
        client.get_json("https://example.com")
