"""Price Agent — fetch price context từ vnstock."""

import logging

from config import DEFAULT_DAYS
from crawlers.vnstock_fetcher import VnstockFetcher
from agents.state import AgentState

logger = logging.getLogger(__name__)
_fetcher = VnstockFetcher()


def price_agent(state: AgentState) -> AgentState:
    ticker = state["ticker"]
    logger.info("Fetching price context for %s", ticker)

    price_context = _fetcher.fetch_price_context(ticker, days=DEFAULT_DAYS)

    return {
        **state,
        "price_context": price_context,
        "need_price_data": False,
    }
