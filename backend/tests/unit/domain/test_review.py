"""Unit tests for day-ahead review generation."""

from datetime import date, time

import pytest

from app.domain.models import Store
from app.domain.review import build_review


def test_review_kpis_and_half_hour_chart_for_default_gate(sample_store: Store):
    review = build_review(sample_store, date(2026, 1, 15), time(9, 0), 4)

    assert review["publishLabel"] == "14 Jan 04:30"
    assert review["decisionLabel"] == "14 Jan, 09:00"
    assert review["kpis"]["peakGw"] == 5.0
    assert review["kpis"]["averageGw"] == 5.0
    assert review["kpis"]["periodCount"] == 48
    assert review["coveredHours"] == 24
    assert review["kpis"]["biasGw"] == 2.0
    assert review["kpis"]["maeGw"] == 2.0
    assert review["kpis"]["rmseGw"] == 2.24
    assert review["kpis"]["nmaePercent"] == 40.0
    assert review["kpis"]["biasLabel"] == "Over-forecast"

    midnight = review["series"][0]
    half = review["series"][1]
    assert midnight["settlementPeriod"] == 1
    assert midnight["label"] == "00:00"
    assert midnight["actualGw"] == 1.0
    assert midnight["forecastGw"] == 5.0
    assert half["settlementPeriod"] == 2
    assert half["label"] == "00:30"
    assert half["actualGw"] == 3.0
    assert half["forecastGw"] == 5.0
    assert midnight["bandLow"] == 3.0
    assert midnight["bandHigh"] == 7.0


def test_delivery_outside_the_decision_window_is_rejected(sample_store: Store):
    with pytest.raises(ValueError, match="outside the January 2026 decision window"):
        build_review(sample_store, date(2026, 1, 1), time(9, 0), 4)


def test_invalid_horizon_hours_is_rejected(sample_store: Store):
    with pytest.raises(ValueError, match="between 0 and 36"):
        build_review(sample_store, date(2026, 1, 15), time(9, 0), 48)


def test_daily_series_has_one_bar_per_january_decision(sample_store: Store):
    review = build_review(sample_store, date(2026, 1, 15), time(9, 0), 4)
    assert len(review["daily"]) == 31
    assert review["daily"][0]["date"] == "2026-01-02"
    assert review["daily"][-1]["date"] == "2026-02-01"
    fifteenth = next(item for item in review["daily"] if item["date"] == "2026-01-15")
    assert fifteenth["maeGw"] == 2.0
