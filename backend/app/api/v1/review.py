"""Review evaluation endpoint."""

from __future__ import annotations

from datetime import date, time

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_current_store
from app.domain.models import Store
from app.domain.study import MAX_HORIZON_HOURS
from app.schemas.review import ReviewResponse
from app.services.review_service import ReviewService, get_review_service

router = APIRouter(tags=["review"])


@router.get("/review", response_model=ReviewResponse)
def review(
    delivery_day: str = Query(alias="deliveryDay"),
    decision_time: str = Query(alias="decisionTime", pattern=r"^\d{2}:\d{2}$"),
    horizon_hours: int = Query(alias="horizonHours", ge=0, le=MAX_HORIZON_HOURS),
    store: Store = Depends(get_current_store),
    service: ReviewService = Depends(get_review_service),
) -> ReviewResponse:
    try:
        delivery = date.fromisoformat(delivery_day)
        clock = time.fromisoformat(decision_time)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Delivery day or decision time is not valid.") from exc

    try:
        data = service.get_review(store, delivery, clock, horizon_hours)
        return ReviewResponse.model_validate(data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
