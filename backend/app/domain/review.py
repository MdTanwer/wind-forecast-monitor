"""Turn Elexon actuals and WINDFOR vintages into a day-ahead review.

The desk locks a bid at a chosen London gate time on the day before delivery.
Only a forecast published at least `horizon_hours` before that gate is eligible.
The vintage used is the latest eligible WINDFOR run.
"""

from __future__ import annotations

from datetime import UTC, date, datetime, time, timedelta
from statistics import mean

from app.domain.metrics import (
    band,
    bias_label,
    error_row,
    gw,
    nmae_percent,
    planning_margin_mw,
    rmse_gw,
)
from app.domain.models import Store
from app.domain.study import (
    DEFAULT_HORIZON_HOURS,
    HORIZON_BUCKETS,
    LONDON,
    MAX_HORIZON_HOURS,
    as_london,
    decision_day,
    delivery_days,
    format_clock,
    format_day,
)
from app.domain.vintage import select_vintage


def _utc(moment: datetime) -> datetime:
    return moment.astimezone(UTC)


def _hour(moment: datetime) -> datetime:
    local = moment.astimezone(LONDON).replace(minute=0, second=0, microsecond=0)
    return local.astimezone(UTC)


def _bucket(lead_hours: float) -> str | None:
    for label, lower, upper in HORIZON_BUCKETS:
        if lower <= lead_hours < upper:
            return label
    return None


def hourly_mean_actuals(actuals: dict[datetime, float]) -> dict[datetime, float]:
    grouped: dict[datetime, list[float]] = {}
    for moment, generation in actuals.items():
        grouped.setdefault(_hour(moment), []).append(generation)
    return {hour: mean(values) for hour, values in grouped.items() if len(values) == 2}


def delivery_series(
    actuals: dict[datetime, float],
    delivery: date,
    vintage: dict[datetime, float],
) -> list[dict]:
    start = as_london(delivery, time(0, 0))
    points: list[dict] = []
    for step in range(48):
        moment = start + timedelta(minutes=30 * step)
        hour = _hour(moment)
        forecast = vintage.get(hour)
        points.append(
            {
                "settlementPeriod": step + 1,
                "hour": hour,
                "time": moment.isoformat(),
                "label": moment.strftime("%H:%M"),
                "actualMw": actuals.get(_utc(moment)),
                "forecastMw": forecast,
            }
        )
    return points


def errors_for_delivery(
    delivery: date,
    store: Store,
    hourly_actual: dict[datetime, float],
    decision_clock: time,
    horizon_hours: int,
) -> dict:
    gate = as_london(decision_day(delivery), decision_clock)
    cutoff = gate - timedelta(hours=horizon_hours)
    _, vintage = select_vintage(store, cutoff)
    errors: list[float] = []
    actuals: list[float] = []
    hour = as_london(delivery, time(0, 0))
    for _ in range(24):
        actual = hourly_actual.get(hour)
        forecast = vintage.get(hour)
        if actual is not None and forecast is not None:
            errors.append(forecast - actual)
            actuals.append(actual)
        hour += timedelta(hours=1)
    return {
        "date": delivery.isoformat(),
        "label": format_day(delivery),
        "errorsMw": errors,
        "actualsMw": actuals,
    }


def horizon_table(store: Store, hourly_actual: dict[datetime, float]) -> list[dict]:
    window = set(delivery_days())
    grouped: dict[str, list[tuple[float, float]]] = {label: [] for label, _, _ in HORIZON_BUCKETS}
    for published, curve in store.forecasts.items():
        for start, forecast in curve.items():
            actual = hourly_actual.get(start)
            if actual is None or start.astimezone(LONDON).date() not in window:
                continue
            lead_hours = (start - published).total_seconds() / 3600
            bucket = _bucket(lead_hours)
            if bucket is None:
                continue
            grouped[bucket].append((forecast - actual, actual))

    return [error_row(label, grouped[label]) for label, _, _ in HORIZON_BUCKETS]


def build_review(
    store: Store,
    delivery: date,
    decision_clock: time,
    horizon_hours: int = DEFAULT_HORIZON_HOURS,
    hourly_actual: dict[datetime, float] | None = None,
    horizons: list[dict] | None = None,
) -> dict:
    if not 0 <= horizon_hours <= MAX_HORIZON_HOURS:
        raise ValueError(f"Minimum forecast horizon must be between 0 and {MAX_HORIZON_HOURS} hours.")
    if delivery not in set(delivery_days()):
        raise ValueError("Delivery day is outside the January 2026 decision window.")

    gate = as_london(decision_day(delivery), decision_clock)
    cutoff = gate - timedelta(hours=horizon_hours)
    vintage_time, vintage = select_vintage(store, cutoff)
    actuals_hourly = hourly_actual if hourly_actual is not None else hourly_mean_actuals(store.actuals)

    series = delivery_series(store.actuals, delivery, vintage)
    covered_hours = len({point["hour"] for point in series if point["forecastMw"] is not None})

    day_errors = [
        errors_for_delivery(day, store, actuals_hourly, decision_clock, horizon_hours)
        for day in delivery_days()
    ]
    scored = [item for item in day_errors if item["errorsMw"]]
    all_errors = [error for item in scored for error in item["errorsMw"]]
    mae_mw = mean(abs(error) for error in all_errors) if all_errors else None
    bias_mw = mean(all_errors) if all_errors else None

    forecast_values = [point["forecastMw"] for point in series if point["forecastMw"] is not None]
    peak_mw = max(forecast_values) if forecast_values else None
    average_mw = mean(forecast_values) if forecast_values else None
    mae_gw = gw(mae_mw, 2)

    rule_pairs = [
        (error, actual)
        for item in scored
        for error, actual in zip(item["errorsMw"], item["actualsMw"], strict=True)
    ]
    margin_mw = planning_margin_mw(all_errors)
    planning_values = (
        [max(0.0, value - margin_mw) for value in forecast_values] if margin_mw is not None else []
    )
    planning_average_mw = mean(planning_values) if planning_values else None

    return {
        "deliveryDay": delivery.isoformat(),
        "deliveryLabel": format_day(delivery),
        "deliveryLabelWithYear": format_day(delivery, with_year=True),
        "decisionLabel": f"{format_day(decision_day(delivery))}, {decision_clock.strftime('%H:%M')}",
        "decisionTime": decision_clock.strftime("%H:%M"),
        "horizonHours": horizon_hours,
        "gateTime": gate.isoformat(),
        "cutoffTime": cutoff.isoformat(),
        "cutoffLabel": format_clock(cutoff),
        "publishTime": vintage_time.isoformat() if vintage_time else None,
        "publishLabel": format_clock(vintage_time) if vintage_time else None,
        "coveredHours": covered_hours,
        "kpis": {
            "peakGw": gw(peak_mw, 1),
            "averageGw": gw(average_mw, 1),
            "periodCount": len(forecast_values),
            "maeGw": mae_gw,
            "rmseGw": rmse_gw(all_errors),
            "nmaePercent": nmae_percent(mae_gw),
            "biasGw": gw(bias_mw, 2),
            "biasLabel": bias_label(bias_mw),
            "scoredDays": len(scored),
        },
        "planning": {
            "marginGw": gw(margin_mw, 2),
            "averageGw": gw(planning_average_mw, 1),
            "forecastAverageGw": gw(average_mw, 1),
            "minimumGw": gw(min(planning_values), 1) if planning_values else None,
        },
        "ruleErrors": error_row("Your rule", rule_pairs),
        "series": [
            {
                "settlementPeriod": point["settlementPeriod"],
                "time": point["time"],
                "label": point["label"],
                "actualGw": gw(point["actualMw"], 2),
                "forecastGw": gw(point["forecastMw"], 2),
                "bandLow": band(point["forecastMw"], mae_mw, -1),
                "bandHigh": band(point["forecastMw"], mae_mw, 1),
                "planningGw": band(point["forecastMw"], margin_mw, -1),
            }
            for point in series
        ],
        "horizons": horizons if horizons is not None else horizon_table(store, actuals_hourly),
        "daily": [
            {
                "date": item["date"],
                "label": item["label"],
                "maeGw": gw(mean(abs(error) for error in item["errorsMw"]), 2)
                if item["errorsMw"]
                else None,
            }
            for item in day_errors
        ],
    }
