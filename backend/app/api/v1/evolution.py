"""Forecast evolution and run-to-run delta endpoint."""

from __future__ import annotations

from datetime import date, time

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_current_store
from app.domain.evolution import build_evolution
from app.domain.models import Store
from app.domain.study import DEFAULT_DECISION_TIME, MAX_HORIZON_HOURS
from app.schemas.evolution import EvolutionResponse

router = APIRouter(tags=["forecasts"])


@router.get("/forecasts/evolution", response_model=EvolutionResponse)
def evolution(
    delivery_day: str = Query(alias="deliveryDay"),
    decision_time: str = Query(default=DEFAULT_DECISION_TIME.strftime("%H:%M"), alias="decisionTime", pattern=r"^\d{2}:\d{2}$"),
    horizon_hours: int = Query(default=0, alias="horizonHours", ge=0, le=MAX_HORIZON_HOURS),
    store: Store = Depends(get_current_store),
) -> EvolutionResponse:
    """Return run-to-run forecast revisions (delta) for a delivery day leading up to gate time."""
    try:
        delivery = date.fromisoformat(delivery_day)
        clock = time.fromisoformat(decision_time)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Delivery day or decision time is not valid.") from exc

    try:
        data = build_evolution(store, delivery, clock, horizon_hours)
        return EvolutionResponse.model_validate(data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
