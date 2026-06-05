"""API endpoint tests."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from api.routes import app, graph, ticker_validator

client = TestClient(app)

SAMPLE_REPORT = {
    "ticker": "HPG",
    "period": "2026-05-28 to 2026-06-04",
    "summary": "Tuần qua HPG ghi nhận kết quả kinh doanh tích cực.",
    "key_events": [{"date": "2026-06-01", "title": "Công bố KQKD Q1", "impact": "high"}],
    "impact_level": "high",
    "risk_flags": ["Rủi ro giá thép"],
    "opportunity_flags": ["Xuất khẩu tăng"],
}


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_analyze_rejects_empty_ticker():
    response = client.post("/analyze", params={"ticker": ""})
    assert response.status_code == 400


def test_analyze_rejects_invalid_ticker_format():
    response = client.post("/analyze", params={"ticker": "HPG!"})
    assert response.status_code == 400


@patch.object(ticker_validator, "is_valid_ticker", return_value=False)
def test_analyze_rejects_unknown_ticker(_mock):
    response = client.post("/analyze", params={"ticker": "ZZZZZ"})
    assert response.status_code == 404


@patch.object(ticker_validator, "is_valid_ticker", return_value=True)
@patch.object(graph, "invoke")
def test_analyze_success(mock_invoke, _mock_valid):
    mock_invoke.return_value = {"final_report": SAMPLE_REPORT}
    response = client.post("/analyze", params={"ticker": "HPG"})
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "HPG"
    assert data["impact_level"] == "high"
    assert len(data["key_events"]) == 1


@patch.object(ticker_validator, "is_valid_ticker", return_value=True)
@patch.object(graph, "invoke")
def test_analyze_no_report(mock_invoke, _mock_valid):
    mock_invoke.return_value = {"final_report": None}
    response = client.post("/analyze", params={"ticker": "HPG"})
    assert response.status_code == 404


def test_serve_index():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
