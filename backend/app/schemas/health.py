"""Pydantic schemas for health and readiness checks."""

from __future__ import annotations

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    mode: str
    upstream: str
    ready: bool
    fetchedAt: str | None = None
