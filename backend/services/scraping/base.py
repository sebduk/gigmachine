"""
Abstract base class for all scrapers.

Each scraper takes a DataSource config and returns a list of
FundingOpportunity-like dicts that the ingestion pipeline
will upsert into the database.
"""
from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Any, Dict, List, Optional

import httpx

from backend.config import settings

logger = logging.getLogger(__name__)


@dataclass
class ScrapedOpportunity:
    """Normalized representation of a scraped funding opportunity."""
    title: str
    url: str
    description: Optional[str] = None
    funder: Optional[str] = None
    institution: Optional[str] = None
    deadline: Optional[date] = None
    budget_min: Optional[Decimal] = None
    budget_max: Optional[Decimal] = None
    currency: str = "USD"
    eligibility_criteria: Optional[str] = None
    career_stages: Optional[str] = None
    external_id: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    fields: List[str] = field(default_factory=list)
    raw_html: Optional[str] = None


class BaseScraper(ABC):
    """Base class for all scrapers. Subclass and implement `scrape()`."""

    def __init__(self, source_url: str, parser_config: Optional[str] = None):
        self.source_url = source_url
        self.config: Dict[str, Any] = json.loads(parser_config) if parser_config else {}

    async def fetch(self, url: Optional[str] = None) -> str:
        """Fetch a URL and return the response body as text."""
        target = url or self.source_url
        async with httpx.AsyncClient(
            headers={"User-Agent": settings.scrape_user_agent},
            follow_redirects=True,
            timeout=30.0,
        ) as client:
            response = await client.get(target)
            response.raise_for_status()
            return response.text

    @abstractmethod
    async def scrape(self) -> List[ScrapedOpportunity]:
        """Scrape the source and return a list of normalized opportunities."""
        ...

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} url={self.source_url!r}>"
