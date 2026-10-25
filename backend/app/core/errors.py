"""Application exceptions and their HTTP exception handler."""

from __future__ import annotations

import logging

from fastapi import Request, status
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class WindWatchError(Exception):
    """Base exception for WindWatch errors."""


class UpstreamServiceError(WindWatchError):
    """Raised when an external data dependency (like Elexon) fails."""


class DataValidationError(WindWatchError):
    """Raised when fetched or parsed data does not satisfy domain constraints."""


async def windwatch_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Map application errors to HTTP responses without leaking internals."""
    if isinstance(exc, UpstreamServiceError):
        logger.error("Upstream service error on %s: %s", request.url.path, exc)
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={"detail": "Upstream Elexon service unavailable. Please retry shortly."},
        )
    logger.error("Unhandled application error on %s: %s", request.url.path, exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal error occurred."},
    )
