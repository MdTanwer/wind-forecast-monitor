"""Data export endpoint for trading desk analysis."""

from __future__ import annotations

import csv
import io
from datetime import date, time

from fastapi import APIRouter, Depends, HTTPException, Query, Response

from app.api.deps import get_current_store
from app.domain.models import Store
from app.domain.study import DEFAULT_DECISION_TIME, DEFAULT_HORIZON_HOURS, MAX_HORIZON_HOURS
from app.services.review_service import ReviewService, get_review_service

router = APIRouter(tags=["export"])


@router.get("/export/review.csv")
def export_review_csv(
    delivery_day: str = Query(alias="deliveryDay"),
    decision_time: str = Query(default=DEFAULT_DECISION_TIME.strftime("%H:%M"), alias="decisionTime", pattern=r"^\d{2}:\d{2}$"),
    horizon_hours: int = Query(default=DEFAULT_HORIZON_HOURS, alias="horizonHours", ge=0, le=MAX_HORIZON_HOURS),
    store: Store = Depends(get_current_store),
    service: ReviewService = Depends(get_review_service),
) -> Response:
    """Export delivery day review timeseries to CSV for trading desk models."""
    try:
        delivery = date.fromisoformat(delivery_day)
        clock = time.fromisoformat(decision_time)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Delivery day or decision time is not valid.") from exc

    try:
        review_data = service.get_review(store, delivery, clock, horizon_hours)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "SettlementPeriod",
        "Timestamp",
        "Label",
        "ActualGW",
        "ForecastGW",
        "PlanningMarginGW",
        "BandLowGW",
        "BandHighGW",
        "ErrorGW",
    ])

    for point in review_data.get("series", []):
        act = point.get("actualGw")
        fc = point.get("forecastGw")
        err = round(fc - act, 2) if (fc is not None and act is not None) else None
        writer.writerow([
            point.get("settlementPeriod", ""),
            point.get("time", ""),
            point.get("label", ""),
            act if act is not None else "",
            fc if fc is not None else "",
            point.get("planningGw", ""),
            point.get("bandLow", ""),
            point.get("bandHigh", ""),
            err if err is not None else "",
        ])

    csv_content = output.getvalue()
    filename = f"windwatch_review_{delivery_day}.csv"
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
