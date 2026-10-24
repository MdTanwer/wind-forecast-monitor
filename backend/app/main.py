"""HTTP API and static hosting for the WindWatch review screen."""

from __future__ import annotations

import logging
import threading
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_v1_router
from app.core.config import get_settings
from app.core.errors import WindWatchError, windwatch_error_handler
from app.core.logging import setup_logging
from app.core.middleware import ProcessTimeMiddleware
from app.services.data_service import get_data_service

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Initialise logging and warm the data cache without blocking startup."""
    settings = get_settings()
    setup_logging(debug=settings.debug)
    logger.info("Starting %s v%s in %s mode", settings.app_title, settings.app_version, settings.app_env)

    service = get_data_service()
    if settings.warmup_on_startup and not service.is_ready():
        logger.info("Initiating background warmup of market data...")
        threading.Thread(target=service.warm_up, daemon=True).start()

    yield
    logger.info("Shutting down %s", settings.app_title)


def _static_dir() -> Path | None:
    candidates = [
        Path(__file__).resolve().parents[1] / "static",
        Path(__file__).resolve().parents[2] / "frontend" / "dist",
    ]
    for candidate in candidates:
        if (candidate / "index.html").exists():
            return candidate
    return None


def create_app() -> FastAPI:
    """Application factory for WindWatch API."""
    settings = get_settings()
    application = FastAPI(
        title=settings.app_title,
        summary="GB day-ahead wind forecast review for January 2026 purchase decisions.",
        version=settings.app_version,
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )

    application.add_middleware(ProcessTimeMiddleware)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["GET"],
        allow_headers=["*"],
    )
    application.add_exception_handler(WindWatchError, windwatch_error_handler)

    # /api is kept as an alias of /api/v1 for the bundled UI; hidden from the schema
    # so OpenAPI does not list every operation twice.
    application.include_router(api_v1_router, prefix="/api/v1")
    application.include_router(api_v1_router, prefix="/api", include_in_schema=False)

    static = _static_dir()
    if static is not None:
        application.mount("/", StaticFiles(directory=static, html=True), name="ui")

    return application


app = create_app()
