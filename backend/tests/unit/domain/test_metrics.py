"""Unit tests for statistical metrics and error calculations."""

from datetime import date, time

from app.domain.metrics import (
    band,
    bias_label,
    error_row,
    gw,
    nmae_percent,
    percentile,
    planning_margin_mw,
    rmse_gw,
)
from app.domain.models import Store
from app.domain.review import build_review


def test_rmse_and_nmae_calculations():
    errors = [1000.0, -1000.0, 2000.0, -2000.0]
    # mean square = (1 + 1 + 4 + 4)/4 * 1000^2 = 2.5 * 1000^2
    # sqrt(2.5 * 10^6) = 1581.138 MW = 1.58 GW
    assert rmse_gw(errors) == 1.58
    assert rmse_gw([]) is None

    assert nmae_percent(1.5, capacity_gw=30.0) == 5.0
    assert nmae_percent(None) is None



def test_percentile_and_planning_margin():
    errors = [100.0, 200.0, 300.0, 400.0, 500.0]
    p50 = percentile(errors, 0.5)
    assert p50 == 300.0

    margin = planning_margin_mw(errors)
    assert margin is not None
    assert margin > 0


def test_gw_and_band_helpers():
    assert gw(1500.0, 1) == 1.5
    assert gw(None, 1) is None
    assert band(5000.0, 1000.0, 1) == 6.0
    assert band(5000.0, 1000.0, -1) == 4.0
    # Floor at 0.0
    assert band(500.0, 1000.0, -1) == 0.0


def test_bias_label_descriptions():
    assert bias_label(None) == "No overlapping actuals"
    assert bias_label(10.0) == "Nearly unbiased"
    assert bias_label(200.0) == "Slight over-forecast"
    assert bias_label(1200.0) == "Over-forecast"
    assert bias_label(-200.0) == "Slight under-forecast"
    assert bias_label(-1200.0) == "Under-forecast"


def test_planning_figure_takes_off_the_p90_over_forecast(sample_store: Store):
    review = build_review(sample_store, date(2026, 1, 15), time(9, 0), 4)
    assert review["planning"]["marginGw"] == 3.0
    assert review["planning"]["averageGw"] == 2.0
    assert review["planning"]["minimumGw"] == 2.0
    assert review["series"][0]["planningGw"] == 2.0


def test_rule_row_scores_only_the_selected_gate_rule(sample_store: Store):
    review = build_review(sample_store, date(2026, 1, 15), time(9, 0), 4)
    rule = review["ruleErrors"]
    assert rule["samples"] == 24
    assert rule["maeGw"] == 2.0
    assert rule["p90Gw"] == 3.0
    assert rule["mape"] == 0.875


def test_horizon_table_buckets_lead_time(sample_store: Store):
    review = build_review(sample_store, date(2026, 1, 15), time(9, 0), 4)
    rows = {row["label"]: row for row in review["horizons"]}
    assert rows["0–6 h"]["samples"] == 1
    assert rows["0–6 h"]["maeGw"] == 0.6
    assert rows["24–48 h"]["samples"] >= 1
    assert rows["6–12 h"]["samples"] == 0
    assert rows["6–12 h"]["maeGw"] is None


def test_error_row_empty_pairs():
    empty = error_row("empty", [])
    assert empty["samples"] == 0
    assert empty["maeGw"] is None
