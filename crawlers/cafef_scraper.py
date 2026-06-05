"""CafeF news scraper."""

import logging
from datetime import datetime, timedelta, timezone

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

LIST_TIMEOUT_SECONDS = (3.05, 15)
ARTICLE_TIMEOUT_SECONDS = (3.05, 12)


class CafeFScraper:
    def __init__(self, ticker, pagesize=20):
        self.ticker = ticker
        self.pagesize = pagesize
        self.base_url = "https://cafef.vn/du-lieu/Ajax/PageNew/News.ashx"
        self.news_types = [0, 4, 5]
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        })

    def get_article_list(self):
        all_articles = []
        for news_type in self.news_types:
            try:
                response = self.session.get(
                    self.base_url,
                    params={
                        "symbol": self.ticker,
                        "NewsType": news_type,
                        "pageIndex": 1,
                        "pageSize": self.pagesize,
                    },
                    timeout=LIST_TIMEOUT_SECONDS,
                )
                response.raise_for_status()
                data = response.json()
                if data.get("Success"):
                    all_articles.extend(data.get("Data", []))
            except (requests.RequestException, ValueError) as e:
                logger.warning("Error fetching NewsType %s for %s: %s", news_type, self.ticker, e)
        return all_articles

    def get_article_content(self, link_detail):
        url = "https://cafef.vn" + link_detail.split("?")[0]
        try:
            response = self.session.get(url, timeout=ARTICLE_TIMEOUT_SECONDS)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.warning("Error fetching article %s: %s", url, e)
            return ""

        soup = BeautifulSoup(response.text, "html.parser")
        content_div = soup.find("div", {"data-role": "content"})
        if not content_div:
            return ""

        paragraphs = content_div.find_all("p")
        return " ".join(p.get_text(strip=True) for p in paragraphs)

    def filter_by_days(self, articles, days=7):
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        filtered = []
        for article in articles:
            try:
                timestamp_ms = int(article["DeployDate"].replace("/Date(", "").replace(")/", ""))
                deploy_date = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)
                if deploy_date >= cutoff:
                    filtered.append(article)
            except (KeyError, TypeError, ValueError) as e:
                logger.warning("Skipping article with invalid DeployDate for %s: %s", self.ticker, e)
        return filtered
