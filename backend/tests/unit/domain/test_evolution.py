"""Unit tests for forecast evolution and delta calculation."""

from datetime import date, time

import pytest

from app.domain.evolution import build_evolution
from app.domain.models import Store


def test_forecast_evolution_tracks_deltas(sample_store: Store):
    evolution = build_evolution(sample_store, date(2026, 1, 15), time(9, 0), horizon_hours=0)

    assert evolution["deliveryDay"] == "2026-01-15"
    assert evolution["decisionTime"] == "09:00"
    assert evolution["latestVintage"] is not None
    assert evolution["latestVintage"]["publishLabel"] == "14 Jan 07:30"
    assert evolution["previousVintage"] is not None
    assert evolution["previousVintage"]["publishLabel"] == "14 Jan 04:30"
    assert evolution["totalVintagesBeforeGate"] == 3

    # Check run comparison on series
    first_sp = evolution["series"][0]
    assert first_sp["settlementPeriod"] == 1
    assert first_sp["label"] == "00:00"
    assert first_sp["actualGw"] == 1.0
    # latest curve in sample_store at 07:30 has curve(9000.0) -> 9.0 GW
    assert first_sp["latestGw"] == 9.0
    # previous curve in sample_store at 04:30 has curve(5000.0) -> 5.0 GW
    assert first_sp["previousGw"] == 5.0
    # delta = 9.0 - 5.0 = 4.0 GW upward revision
    assert first_sp["deltaGw"] == 4.0


def test_evolution_outside_window_raises(sample_store: Store):
    with pytest.raises(ValueError, match="outside the January 2026 decision window"):
        build_evolution(sample_store, date(2026, 1, 1), time(9, 0))
