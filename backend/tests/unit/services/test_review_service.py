"""Unit tests for ReviewService caching, bounds, and invalidation."""

from datetime import date, time

from app.domain.models import Store
from app.services.review_service import ReviewService
from tests.conftest import build_sample_store


def test_review_service_memoizes_evaluations(sample_store: Store):
    review_svc = ReviewService()
    first = review_svc.get_review(sample_store, date(2026, 1, 15), time(9, 0), 4)
    second = review_svc.get_review(sample_store, date(2026, 1, 15), time(9, 0), 4)
    assert first is second


def test_review_service_cache_is_bounded(sample_store: Store):
    review_svc = ReviewService(max_entries=2)
    for horizon in (0, 2, 4):
        review_svc.get_review(sample_store, date(2026, 1, 15), time(9, 0), horizon)
    assert len(review_svc._reviews) == 2


def test_review_service_invalidates_on_new_store():
    review_svc = ReviewService()
    first = review_svc.get_review(build_sample_store(), date(2026, 1, 15), time(9, 0), 4)
    second = review_svc.get_review(build_sample_store(), date(2026, 1, 15), time(9, 0), 4)
    assert first is not second
