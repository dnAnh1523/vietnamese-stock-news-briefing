"""Scraper Agent - fetch tin tức từ CafeF."""

import logging

from config import MAX_RETRIES, DEFAULT_DAYS, DEFAULT_PAGESIZE
from crawlers.cafef_scraper import CafeFScraper
from agents.state import AgentState

logger = logging.getLogger(__name__)


def _dedupe_articles(articles: list[dict]) -> list[dict]:
    seen = set()
    unique = []
    for article in articles:
        key = article.get("LinkDetail") or article.get("Title")
        if key and key not in seen:
            seen.add(key)
            unique.append(article)
    return unique


def _merge_articles(existing: list[dict], new: list[dict]) -> list[dict]:
    return _dedupe_articles(existing + new)


def scraper_agent(state: AgentState) -> AgentState:
    ticker = state["ticker"]
    retry_count = state["retry_count"]

    if retry_count >= MAX_RETRIES:
        logger.warning("Max retries reached for %s", ticker)
        return {**state, "need_more_data": False}

    days = DEFAULT_DAYS + retry_count * DEFAULT_DAYS
    logger.info("Scraping CafeF for %s (window=%d days, attempt=%d)", ticker, days, retry_count + 1)

    scraper = CafeFScraper(ticker, pagesize=DEFAULT_PAGESIZE)
    articles = scraper.get_article_list()
    articles = scraper.filter_by_days(articles, days=days)
    articles = _merge_articles(state.get("articles", []), articles)

    for article in articles:
        if not article.get("content"):
            article["content"] = scraper.get_article_content(article["LinkDetail"])

    return {
        **state,
        "articles": articles,
        "retry_count": retry_count + 1,
        "need_more_data": False,
    }
