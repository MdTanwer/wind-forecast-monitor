"""Pydantic schemas for the review API."""

from __future__ import annotations

from pydantic import BaseModel


class Kpis(BaseModel):
    peakGw: float | None
    averageGw: float | None
    periodCount: int
    maeGw: float | None
    rmseGw: float | None = None
    nmaePercent: float | None = None
    biasGw: float | None
    biasLabel: str
    scoredDays: int


class Planning(BaseModel):
    marginGw: float | None
    averageGw: float | None
    forecastAverageGw: float | None
    minimumGw: float | None


class RuleErrors(BaseModel):
    label: str
    maeGw: float | None
    rmseGw: float | None = None
    p90Gw: float | None
    mape: float | None
    nmaePercent: float | None = None
    samples: int


class SeriesPoint(BaseModel):
    settlementPeriod: int | None = None
    time: str
    label: str
    actualGw: float | None
    forecastGw: float | None
    bandLow: float | None
    bandHigh: float | None
    planningGw: float | None


class HorizonRow(BaseModel):
    label: str
    maeGw: float | None
    rmseGw: float | None = None
    p90Gw: float | None
    mape: float | None
    nmaePercent: float | None = None
    samples: int


class DailyItem(BaseModel):
    date: str
    label: str
    maeGw: float | None


class ReviewResponse(BaseModel):
    deliveryDay: str
    deliveryLabel: str
    deliveryLabelWithYear: str
    decisionLabel: str
    decisionTime: str
    horizonHours: int
    gateTime: str
    cutoffTime: str
    cutoffLabel: str
    publishTime: str | None
    publishLabel: str | None
    coveredHours: int
    kpis: Kpis
    planning: Planning
    ruleErrors: RuleErrors
    series: list[SeriesPoint]
    horizons: list[HorizonRow]
    daily: list[DailyItem]
