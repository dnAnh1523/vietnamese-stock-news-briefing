"""Project configuration."""

import logging

MAX_RETRIES = 3
MIN_ARTICLES = 3
DEFAULT_PAGESIZE = 20
DEFAULT_DAYS = 7

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
