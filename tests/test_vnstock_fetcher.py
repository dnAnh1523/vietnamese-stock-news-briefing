"""vnstock fetcher tests."""

from unittest.mock import MagicMock, patch

import pandas as pd

from crawlers.vnstock_fetcher import VnstockFetcher


def test_is_valid_ticker_true():
    fetcher = VnstockFetcher()
    with patch.object(fetcher, "get_exchange", return_value="hose"):
        assert fetcher.is_valid_ticker("HPG") is True


def test_is_valid_ticker_false():
    fetcher = VnstockFetcher()
    with patch.object(fetcher, "get_exchange", return_value=None):
        assert fetcher.is_valid_ticker("ZZZZZ") is False


@patch("crawlers.vnstock_fetcher.Quote")
def test_fetch_price_context_success(mock_quote_cls):
    mock_df = pd.DataFrame({
        "close": [100.0, 105.0, 110.0],
    })
    mock_quote_cls.return_value.history.return_value = mock_df

    fetcher = VnstockFetcher()
    with patch.object(fetcher, "get_exchange", return_value="hose"):
        result = fetcher.fetch_price_context("HPG")

    assert result["ticker"] == "HPG"
    assert result["exchange"] == "hose"
    assert result["latest_close"] == 110.0
    assert result["week_change_pct"] == 10.0


def test_fetch_price_context_invalid_ticker():
    fetcher = VnstockFetcher()
    with patch.object(fetcher, "get_exchange", return_value=None):
        result = fetcher.fetch_price_context("INVALID")
    assert "error" in result
