"""HTTP contract tests for the WindWatch API (served at /api/v1 and /api)."""

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_current_store
from app.core.errors import UpstreamServiceError
from app.main import app

PREFIXES = ("/api/v1", "/api")
REVIEW_PARAMS: dict[str, str | int] = {"deliveryDay": "2026-01-15", "decisionTime": "09:00", "horizonHours": 4}


@pytest.mark.parametrize("prefix", PREFIXES)
def test_health(client: TestClient, prefix: str):
    response = client.get(f"{prefix}/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["mode"] == "dynamic_live_api"
    assert "upstream" in body
    assert "x-process-time" in response.headers


@pytest.mark.parametrize("prefix", PREFIXES)
def test_readiness(client: TestClient, prefix: str):
    assert client.get(f"{prefix}/ready").status_code in (200, 503)


@pytest.mark.parametrize("prefix", PREFIXES)
def test_meta_lists_the_31_delivery_days(client: TestClient, prefix: str):
    body = client.get(f"{prefix}/meta").json()
    assert len(body["deliveryDays"]) == 31
    assert body["deliveryDays"][0]["value"] == "2026-01-02"
    assert body["deliveryDays"][-1]["value"] == "2026-02-01"
    assert body["defaultDeliveryDay"] == "2026-01-15"
    assert body["defaultDecisionTime"] == "09:00"
    assert body["timezone"] == "Europe/London"
    assert body["liveApi"] is True
    assert "Elexon" in body["source"]


@pytest.mark.parametrize("prefix", PREFIXES)
def test_default_review_uses_the_0430_run(client: TestClient, prefix: str):
    response = client.get(f"{prefix}/review", params=REVIEW_PARAMS)
    assert response.status_code == 200
    body = response.json()
    assert body["publishLabel"] == "14 Jan 04:30"
    assert "kpis" in body
    assert body["kpis"]["rmseGw"] == 2.24
    assert body["kpis"]["nmaePercent"] == 6.7
    assert len(body["series"]) == 48
    assert body["series"][0]["settlementPeriod"] == 1
    assert len(body["daily"]) == 31


@pytest.mark.parametrize("prefix", PREFIXES)
def test_forecast_evolution_endpoint(client: TestClient, prefix: str):
    response = client.get(f"{prefix}/forecasts/evolution", params={"deliveryDay": "2026-01-15", "decisionTime": "09:00"})
    assert response.status_code == 200
    body = response.json()
    assert body["latestVintage"]["publishLabel"] == "14 Jan 07:30"
    assert len(body["series"]) == 48
    assert body["series"][0]["settlementPeriod"] == 1
    assert body["series"][0]["deltaGw"] == 4.0


@pytest.mark.parametrize("prefix", PREFIXES)
def test_export_review_csv_endpoint(client: TestClient, prefix: str):
    response = client.get(f"{prefix}/export/review.csv", params=REVIEW_PARAMS)
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert "SettlementPeriod,Timestamp,Label" in response.text



def test_delivery_outside_the_window_is_a_400(client: TestClient):
    response = client.get("/api/review", params={**REVIEW_PARAMS, "deliveryDay": "2026-01-01"})
    assert response.status_code == 400


def test_impossible_clock_time_is_a_400(client: TestClient):
    response = client.get("/api/review", params={**REVIEW_PARAMS, "decisionTime": "25:00"})
    assert response.status_code == 400


def test_badly_formed_time_is_rejected(client: TestClient):
    response = client.get("/api/review", params={**REVIEW_PARAMS, "decisionTime": "9am"})
    assert response.status_code == 422


def test_upstream_failure_is_a_502_without_leaking_details():
    def failing_store():
        raise UpstreamServiceError("secret internal detail")

    app.dependency_overrides[get_current_store] = failing_store
    try:
        response = TestClient(app).get("/api/meta")
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 502
    assert "secret" not in response.text


def test_openapi_lists_each_operation_once(client: TestClient):
    paths = client.get("/api/openapi.json").json()["paths"]
    assert "/api/v1/review" in paths
    assert "/api/review" not in paths
