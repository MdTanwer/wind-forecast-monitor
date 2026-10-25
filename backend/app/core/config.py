"""Application settings and configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import date, time
from functools import lru_cache
from pathlib import Path

from app.domain.study import (
    DEFAULT_DECISION_TIME,
    DEFAULT_DELIVERY_DAY,
    DEFAULT_HORIZON_HOURS,
    DELIVERY_END,
    DELIVERY_START,
)

_TRUTHY = ("1", "true", "yes")


def _env_bool(name: str, default: str) -> bool:
    return os.getenv(name, default).strip().lower() in _TRUTHY


def _env_int(name: str, default: int) -> int:
    return int(os.getenv(name, str(default)))


def _env_list(name: str, default: str) -> list[str]:
    return [item.strip() for item in os.getenv(name, default).split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    """Runtime configuration loaded from environment variables."""

    # Environment
    app_env: str = field(default_factory=lambda: os.getenv("APP_ENV", "production"))
    debug: bool = field(default_factory=lambda: _env_bool("DEBUG", "false"))
    app_title: str = "WindWatch"
    app_version: str = "2.0.0"

    # CORS (only needed when the UI is served from a different origin, e.g. Vite dev server)
    cors_origins: list[str] = field(
        default_factory=lambda: _env_list("CORS_ORIGINS", "http://127.0.0.1:5173,http://localhost:5173")
    )

    # Elexon BMRS API
    elexon_fuelhh_url: str = field(
        default_factory=lambda: os.getenv(
            "ELEXON_FUELHH_URL",
            "https://data.elexon.co.uk/bmrs/api/v1/datasets/FUELHH/stream",
        )
    )
    elexon_windfor_url: str = field(
        default_factory=lambda: os.getenv(
            "ELEXON_WINDFOR_URL",
            "https://data.elexon.co.uk/bmrs/api/v1/datasets/WINDFOR/stream",
        )
    )
    elexon_user_agent: str = "windwatch/2.0 (production day-ahead wind monitor; live dynamic client)"
    elexon_timeout_seconds: int = field(default_factory=lambda: _env_int("ELEXON_TIMEOUT_SECONDS", 30))
    elexon_max_retries: int = field(default_factory=lambda: max(1, _env_int("ELEXON_MAX_RETRIES", 3)))

    # Cache & snapshot
    cache_ttl_seconds: int = field(default_factory=lambda: _env_int("CACHE_TTL_SECONDS", 900))
    data_dir: Path = field(
        default_factory=lambda: Path(os.getenv("DATA_DIR", str(Path(__file__).resolve().parents[2] / "data")))
    )
    snapshot_filename: str = field(default_factory=lambda: os.getenv("SNAPSHOT_FILENAME", "elexon_snapshot.json"))
    warmup_on_startup: bool = field(default_factory=lambda: _env_bool("WARMUP_ON_STARTUP", "true"))

    # Study window (single source of truth lives in app.domain.study)
    delivery_start: date = DELIVERY_START
    delivery_end: date = DELIVERY_END
    default_delivery_day: date = DEFAULT_DELIVERY_DAY
    default_decision_time: time = DEFAULT_DECISION_TIME
    default_horizon_hours: int = DEFAULT_HORIZON_HOURS

    @property
    def snapshot_path(self) -> Path:
        return self.data_dir / self.snapshot_filename


@lru_cache
def get_settings() -> Settings:
    """Process-wide settings instance."""
    return Settings()
