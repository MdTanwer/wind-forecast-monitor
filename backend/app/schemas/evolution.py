"""Pydantic schemas for the forecast evolution and delta API."""

from __future__ import annotations

from pydantic import BaseModel


class VintageSummary(BaseModel):
    publishTime: str
    publishLabel: str
    leadHoursToGate: float
    averageGw: float | None
    peakGw: float | None


class EvolutionPoint(BaseModel):
    settlementPeriod: int
    time: str
    label: str
    actualGw: float | None
    latestGw: float | None
    previousGw: float | None
    deltaGw: float | None


class EvolutionResponse(BaseModel):
    deliveryDay: str
    deliveryLabel: str
    decisionTime: str
    gateTime: str
    latestVintage: VintageSummary | None
    previousVintage: VintageSummary | None
    totalVintagesBeforeGate: int
    series: list[EvolutionPoint]
