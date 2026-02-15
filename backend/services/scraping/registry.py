"""
Scraper registry — maps parser_class_name strings to scraper classes.

When a DataSource has parser_class_name="rss", the registry resolves
it to RssScraper. Add new scrapers here as you build them.
"""
from __future__ import annotations

from typing import Dict, Type

from backend.services.scraping.base import BaseScraper
from backend.services.scraping.rss_scraper import RssScraper
from backend.services.scraping.web_scraper import WebScraper
from backend.services.scraping.api_scraper import ApiScraper

# Short name -> class mapping
_REGISTRY: Dict[str, Type[BaseScraper]] = {
    "rss": RssScraper,
    "web": WebScraper,
    "api": ApiScraper,
}


def register_scraper(name: str, cls: Type[BaseScraper]) -> None:
    """Register a new scraper class under a short name."""
    _REGISTRY[name] = cls


def get_scraper(parser_class_name: str, source_url: str, parser_config: str | None = None) -> BaseScraper:
    """Instantiate a scraper by its registered name."""
    cls = _REGISTRY.get(parser_class_name)
    if cls is None:
        raise ValueError(
            f"Unknown scraper '{parser_class_name}'. "
            f"Available: {list(_REGISTRY.keys())}"
        )
    return cls(source_url=source_url, parser_config=parser_config)
