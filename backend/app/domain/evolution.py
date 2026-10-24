"""Domain logic for tracking forecast evolution and run-to-run deltas."""

from __future__ import annotations

from datetime import UTC, date, datetime, time, timedelta
from statistics import mean

from app.domain.metrics import gw
from app.domain.models import Store
from app.domain.study import (
    LONDON,
    as_london,
    decision_day,
    delivery_days,
    format_clock,
    format_day,
)


def _utc(moment: datetime) -> datetime:
    return moment.astimezone(UTC)


def _hour(moment: datetime) -> datetime:
    local = moment.astimezone(LONDON).replace(minute=0, second=0, microsecond=0)
    return local.astimezone(UTC)


def _vintage_summary(
    published: datetime | None,
    curve: dict[datetime, float] | None,
    delivery: date,
    gate: datetime,
) -> dict | None:
    if published is None or curve is None:
        return None
    start = as_london(delivery, time(0, 0))
    values = [
        curve[start + timedelta(hours=h)]
        for h in range(24)
        if (start + timedelta(hours=h)) in curve
    ]
    if not values:
        return None
    lead_hours = round((gate - published).total_seconds() / 3600.0, 1)
    return {
        "publishTime": published.isoformat(),
        "publishLabel": format_clock(published),
        "leadHoursToGate": lead_hours,
        "averageGw": gw(mean(values), 2),
        "peakGw": gw(max(values), 2),
    }


def build_evolution(
    store: Store,
    delivery: date,
    decision_clock: time,
    horizon_hours: int = 0,
) -> dict:
    """Compare the latest eligible forecast run against the previous run before gate time."""
    if delivery not in set(delivery_days()):
        raise ValueError("Delivery day is outside the January 2026 decision window.")

    gate = as_london(decision_day(delivery), decision_clock)
    cutoff = gate - timedelta(hours=horizon_hours)

    eligible_pubs = [p for p in store._publish_times if p <= cutoff]
    latest_pub = eligible_pubs[-1] if eligible_pubs else None
    prev_pub = eligible_pubs[-2] if len(eligible_pubs) >= 2 else None

    latest_curve = store.forecasts.get(latest_pub, {}) if latest_pub else {}
    prev_curve = store.forecasts.get(prev_pub, {}) if prev_pub else {}

    start = as_london(delivery, time(0, 0))
    points: list[dict] = []
    for step in range(48):
        moment = start + timedelta(minutes=30 * step)
        hour = _hour(moment)
        actual_mw = store.actuals.get(_utc(moment))
        latest_mw = latest_curve.get(hour)
        prev_mw = prev_curve.get(hour)

        actual_gw = gw(actual_mw, 2)
        latest_gw = gw(latest_mw, 2)
        prev_gw = gw(prev_mw, 2)
        delta_gw = round(latest_gw - prev_gw, 2) if (latest_gw is not None and prev_gw is not None) else None

        points.append(
            {
                "settlementPeriod": step + 1,
                "time": moment.isoformat(),
                "label": moment.strftime("%H:%M"),
                "actualGw": actual_gw,
                "latestGw": latest_gw,
                "previousGw": prev_gw,
                "deltaGw": delta_gw,
            }
        )

    return {
        "deliveryDay": delivery.isoformat(),
        "deliveryLabel": format_day(delivery, with_year=True),
        "decisionTime": decision_clock.strftime("%H:%M"),
        "gateTime": gate.isoformat(),
        "latestVintage": _vintage_summary(latest_pub, latest_curve, delivery, gate),
        "previousVintage": _vintage_summary(prev_pub, prev_curve, delivery, gate),
        "totalVintagesBeforeGate": len(eligible_pubs),
        "series": points,
    }
