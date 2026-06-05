"""vnstock price and market data fetcher."""

import logging
from datetime import datetime, timedelta, timezone

from vnstock import Quote, Reference

logger = logging.getLogger(__name__)


class VnstockFetcher:
    def __init__(self):
        self.ref = Reference()
        self._exchange_map = None

    def _load_exchange_map(self):
        if self._exchange_map is None:
            df = self.ref.equity.list_by_exchange()
            self._exchange_map = dict(zip(df["symbol"], df["exchange"].str.lower()))
        return self._exchange_map

    def is_valid_ticker(self, ticker: str) -> bool:
        return self.get_exchange(ticker) is not None

    def get_exchange(self, ticker: str) -> str | None:
        exchange_map = self._load_exchange_map()
        return exchange_map.get(ticker.upper())

    def fetch_price_context(self, ticker: str, days: int = 7) -> dict:
        ticker = ticker.upper()
        exchange = self.get_exchange(ticker)
        if not exchange:
            return {"ticker": ticker, "error": "Mã cổ phiếu không hợp lệ"}

        end = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        start = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")

        try:
            quote = Quote(symbol=ticker, source="vci", show_log=False)
            df = quote.history(start=start, end=end)

            if df is None or df.empty:
                return {
                    "ticker": ticker,
                    "exchange": exchange,
                    "error": "Không có dữ liệu giá trong khoảng thời gian yêu cầu",
                }

            close_col = "close" if "close" in df.columns else "Close"
            latest = df.iloc[-1]
            first = df.iloc[0]
            latest_close = float(latest[close_col])
            first_close = float(first[close_col])
            change_pct = ((latest_close - first_close) / first_close) * 100 if first_close else 0.0

            return {
                "ticker": ticker,
                "exchange": exchange,
                "latest_close": latest_close,
                "week_change_pct": round(change_pct, 2),
                "period_start": start,
                "period_end": end,
                "trading_days": len(df),
            }
        except Exception as e:
            logger.warning("vnstock fetch failed for %s: %s", ticker, e)
            return {"ticker": ticker, "exchange": exchange, "error": str(e)}
