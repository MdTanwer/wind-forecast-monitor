"""Unit tests for vintage selection and publication matching."""

from datetime import UTC, datetime

from app.domain.models import Store
from app.domain.vintage import select_vintage


def test_select_vintage_with_four_hour_horizon(sample_store: Store):
    """At 09:00 decision with 4h horizon (05:00 cutoff), 04:30 run is selected."""
    cutoff = datetime(2026, 1, 14, 5, 0, tzinfo=UTC)
    published, vintage = select_vintage(sample_store, cutoff)
    assert published == datetime(2026, 1, 14, 4, 30, tzinfo=UTC)
    hour_target = datetime(2026, 1, 15, 0, 0, tzinfo=UTC)
    assert vintage[hour_target] == 5000.0


def test_select_vintage_with_zero_horizon(sample_store: Store):
    """At 09:00 decision with 0h horizon (09:00 cutoff), 07:30 run is eligible."""
    cutoff = datetime(2026, 1, 14, 9, 0, tzinfo=UTC)
    published, vintage = select_vintage(sample_store, cutoff)
    assert published == datetime(2026, 1, 14, 7, 30, tzinfo=UTC)
    hour_target = datetime(2026, 1, 15, 0, 0, tzinfo=UTC)
    assert vintage[hour_target] == 9000.0


def test_select_vintage_before_any_publication(sample_store: Store):
    """Cutoff before all published vintages returns None and empty dictionary."""
    cutoff = datetime(2026, 1, 1, 0, 0, tzinfo=UTC)
    published, vintage = select_vintage(sample_store, cutoff)
    assert published is None
    assert vintage == {}
