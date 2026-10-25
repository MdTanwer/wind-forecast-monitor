"""API v1 router composition."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.evolution import router as evolution_router
from app.api.v1.export import router as export_router
from app.api.v1.health import router as health_router
from app.api.v1.meta import router as meta_router
from app.api.v1.review import router as review_router

api_v1_router = APIRouter()
api_v1_router.include_router(health_router)
api_v1_router.include_router(meta_router)
api_v1_router.include_router(review_router)
api_v1_router.include_router(evolution_router)
api_v1_router.include_router(export_router)
