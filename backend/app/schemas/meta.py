"""Pydantic schemas for metadata endpoints."""

from __future__ import annotations

from pydantic import BaseModel


class DeliveryDayItem(BaseModel):
    value: str
    label: str


class SourcesInfo(BaseModel):
    actuals: str
    forecasts: str


class MetaResponse(BaseModel):
    deliveryDays: list[DeliveryDayItem]
    defaultDeliveryDay: str
    defaultDecisionTime: str
    defaultHorizonHours: int
    horizonOptions: list[int]
    timezone: str
    fetchedAt: str
    source: str
    liveApi: bool
    actualHalfHours: int
    forecastPublications: int
    sources: SourcesInfo
