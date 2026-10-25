"""Metadata endpoint detailing available study days and source descriptions."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import get_current_store
from app.core.config import Settings, get_settings
from app.domain.models import Store
from app.domain.study import HORIZON_OPTIONS, LONDON, delivery_days, format_day
from app.schemas.meta import DeliveryDayItem, MetaResponse, SourcesInfo

router = APIRouter(tags=["meta"])


@router.get("/meta", response_model=MetaResponse)
def meta(
    store: Store = Depends(get_current_store),
    settings: Settings = Depends(get_settings),
) -> MetaResponse:
    return MetaResponse(
        deliveryDays=[
            DeliveryDayItem(value=day.isoformat(), label=format_day(day, with_year=True)) for day in delivery_days()
        ],
        defaultDeliveryDay=settings.default_delivery_day.isoformat(),
        defaultDecisionTime=settings.default_decision_time.strftime("%H:%M"),
        defaultHorizonHours=settings.default_horizon_hours,
        horizonOptions=list(HORIZON_OPTIONS),
        timezone=LONDON.key,
        fetchedAt=store.fetched_at,
        source=store.source,
        liveApi=True,
        actualHalfHours=len(store.actuals),
        forecastPublications=len(store.forecasts),
        sources=SourcesInfo(
            actuals="Elexon FUELHH fuelType WIND (/datasets/FUELHH/stream)",
            forecasts="Elexon WINDFOR (/datasets/WINDFOR/stream)",
        ),
    )
