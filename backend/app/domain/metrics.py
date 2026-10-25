"""Statistical metrics and calculations for forecast error scoring."""

from __future__ import annotations

import math
from statistics import mean

MW_PER_GW = 1000.0
# National wind below this is too small for a stable percentage error.
MAPE_FLOOR_MW = 100.0


def percentile(values: list[float], fraction: float) -> float:
    """Compute percentile using linear interpolation between closest ranks."""
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = fraction * (len(ordered) - 1)
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def gw(megawatts: float | None, digits: int) -> float | None:
    """Convert MW to GW rounded to the requested number of decimal digits."""
    if megawatts is None:
        return None
    return round(megawatts / MW_PER_GW, digits)


def rmse_gw(errors_mw: list[float]) -> float | None:
    """Calculate Root Mean Square Error (RMSE) in GW rounded to 2 decimal places."""
    if not errors_mw:
        return None
    mean_sq = mean(err**2 for err in errors_mw)
    return round(math.sqrt(mean_sq) / MW_PER_GW, 2)


def nmae_percent(mae_gw: float | None, capacity_gw: float | None = None) -> float | None:
    """Normalized MAE as a percentage of capacity (strictly derived from Elexon actuals)."""
    if mae_gw is None or capacity_gw is None or capacity_gw <= 0:
        return None
    return round((mae_gw / capacity_gw) * 100, 1)


def band(forecast_mw: float | None, mae_mw: float | None, sign: int) -> float | None:
    """Calculate lower or upper error band in GW, floored at 0.0."""
    if forecast_mw is None or mae_mw is None:
        return None
    return round(max(0.0, forecast_mw + sign * mae_mw) / MW_PER_GW, 2)


def bias_label(bias_mw: float | None) -> str:
    """Return descriptive classification of forecast bias."""
    if bias_mw is None:
        return "No overlapping actuals"
    bias_gw = bias_mw / MW_PER_GW
    if abs(bias_gw) < 0.05:
        return "Nearly unbiased"
    slight = abs(bias_gw) < 0.75
    if bias_gw < 0:
        return "Slight under-forecast" if slight else "Under-forecast"
    return "Slight over-forecast" if slight else "Over-forecast"


def planning_margin_mw(errors: list[float]) -> float | None:
    """Over-forecast exceeded in only one scored hour in ten (P90 of forecast − actual)."""
    if not errors:
        return None
    return max(0.0, percentile(errors, 0.9))


def error_row(label: str, pairs: list[tuple[float, float]], capacity_gw: float | None = None) -> dict:
    """MAE, RMSE, P90 absolute error, MAPE and nMAE for (forecast − actual, actual) pairs in MW."""
    if not pairs:
        return {
            "label": label,
            "maeGw": None,
            "rmseGw": None,
            "p90Gw": None,
            "mape": None,
            "nmaePercent": None,
            "samples": 0,
        }
    errors = [error for error, _ in pairs]
    absolute = [abs(error) for error in errors]
    mape_terms = [abs(error) / actual for error, actual in pairs if actual >= MAPE_FLOOR_MW]
    mae_in_gw = gw(mean(absolute), 2)
    eff_capacity_gw = capacity_gw if capacity_gw is not None else gw(max(act for _, act in pairs), 2)
    return {
        "label": label,
        "maeGw": mae_in_gw,
        "rmseGw": rmse_gw(errors),
        "p90Gw": gw(percentile(absolute, 0.9), 2),
        "mape": round(mean(mape_terms), 3) if mape_terms else None,
        "nmaePercent": nmae_percent(mae_in_gw, eff_capacity_gw),
        "samples": len(pairs),
    }
