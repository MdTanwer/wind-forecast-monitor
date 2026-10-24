"""Health and readiness check endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status

from app.core.config import Settings, get_settings
from app.schemas.health import HealthResponse
from app.services.data_service import DataService, get_data_service

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health(
    settings: Settings = Depends(get_settings),
    service: DataService = Depends(get_data_service),
) -> HealthResponse:
    store = service.cached_store
    return HealthResponse(
        status="ok",
        mode="dynamic_live_api",
        upstream=settings.elexon_fuelhh_url.rsplit("/datasets", 1)[0],
        ready=service.is_ready(),
        fetchedAt=store.fetched_at if store else None,
    )


@router.get("/ready")
def readiness(
    response: Response,
    service: DataService = Depends(get_data_service),
) -> dict:
    if not service.is_ready():
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "warming_up", "ready": False}
    return {"status": "ready", "ready": True}
