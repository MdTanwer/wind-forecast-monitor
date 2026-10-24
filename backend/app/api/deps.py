"""FastAPI dependency providers."""

from __future__ import annotations

from fastapi import Depends

from app.domain.models import Store
from app.services.data_service import DataService, get_data_service


def get_current_store(service: DataService = Depends(get_data_service)) -> Store:
    """Return the latest market data.

    `UpstreamServiceError` is mapped to HTTP 502 by the global exception handler.
    """
    return service.get_store()
