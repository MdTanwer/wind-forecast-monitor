"""Logging configuration for production and development."""

from __future__ import annotations

import logging
import sys


def setup_logging(debug: bool = False) -> None:
    """Configure root and app loggers with standard format."""
    level = logging.DEBUG if debug else logging.INFO
    log_format = "%(asctime)s [%(levelname)s] [%(name)s]: %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    logging.basicConfig(
        level=level,
        format=log_format,
        datefmt=date_format,
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )
