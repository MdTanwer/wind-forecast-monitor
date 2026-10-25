"""HTTP client for Elexon BMRS API."""

from __future__ import annotations

import json
import logging
import time
import urllib.error
import urllib.request
from datetime import UTC, datetime

from app.core.config import get_settings
from app.core.errors import UpstreamServiceError

logger = logging.getLogger(__name__)

# Never let a server-supplied Retry-After stall a fetch worker for longer than this.
MAX_RETRY_AFTER_SECONDS = 60.0


def parse_iso(value: str) -> datetime:
    """Parse ISO8601 string to timezone-aware UTC datetime."""
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)


def stamp_utc(moment: datetime) -> str:
    """Format datetime as UTC ISO8601 string."""
    return moment.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def extract_rows(payload: list | dict) -> list[dict]:
    """Extract list of records whether response is raw array or wrapped in {data: [...]}."""
    if isinstance(payload, dict):
        data = payload.get("data", [])
        return data if isinstance(data, list) else []
    return payload if isinstance(payload, list) else []


class ElexonClient:
    """Client for Elexon BMRS API with retry, backoff, and timeout control."""

    def __init__(
        self,
        user_agent: str | None = None,
        timeout: int | None = None,
        max_retries: int | None = None,
    ) -> None:
        settings = get_settings()
        self.user_agent = user_agent if user_agent is not None else settings.elexon_user_agent
        self.timeout = timeout if timeout is not None else settings.elexon_timeout_seconds
        self.max_retries = max(1, max_retries if max_retries is not None else settings.elexon_max_retries)

    def get_json(self, url: str) -> list | dict:
        """Fetch and parse JSON with retries, Retry-After support and exponential backoff."""
        request = urllib.request.Request(
            url,
            headers={"Accept": "application/json", "User-Agent": self.user_agent},
        )
        last_err: Exception | None = None

        for attempt in range(self.max_retries):
            wait_time = float(2**attempt)
            try:
                with urllib.request.urlopen(request, timeout=self.timeout) as response:
                    return json.loads(response.read().decode("utf-8"))
            except urllib.error.HTTPError as exc:
                last_err = exc
                # Client errors other than 429 will not succeed on retry.
                if 400 <= exc.code < 500 and exc.code != 429:
                    logger.error("Non-retryable HTTP %d from Elexon: %s", exc.code, url)
                    raise UpstreamServiceError(f"Elexon HTTP {exc.code} for {url}") from exc
                retry_after = exc.headers.get("Retry-After") if exc.headers else None
                if retry_after and retry_after.isdigit():
                    wait_time = min(float(retry_after), MAX_RETRY_AFTER_SECONDS)
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
                last_err = exc

            if attempt < self.max_retries - 1:
                logger.warning(
                    "Elexon request attempt %d/%d failed for %s: %s (retrying in %.1fs)",
                    attempt + 1,
                    self.max_retries,
                    url,
                    last_err,
                    wait_time,
                )
                time.sleep(wait_time)

        raise UpstreamServiceError(f"Elexon API request failed after {self.max_retries} attempts: {url}") from last_err
