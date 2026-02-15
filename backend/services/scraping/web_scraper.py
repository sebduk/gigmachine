"""Generic web scraper using CSS selectors configured per data source."""
from __future__ import annotations

import logging
from typing import List

from bs4 import BeautifulSoup

from backend.services.scraping.base import BaseScraper, ScrapedOpportunity
from backend.utils.text import extract_keywords

logger = logging.getLogger(__name__)


class WebScraper(BaseScraper):
    """Scrape funding opportunities from web pages using CSS selectors.

    Parser config (JSON):
        item_selector: str — CSS selector for each opportunity item
        title_selector: str — CSS selector for title within item
        link_selector: str — CSS selector for link within item
        description_selector: str — CSS selector for description within item (optional)
        deadline_selector: str — CSS selector for deadline text (optional)
        funder: str — override funder name
        base_url: str — base URL for relative links
    """

    async def scrape(self) -> List[ScrapedOpportunity]:
        raw = await self.fetch()
        soup = BeautifulSoup(raw, "html.parser")

        item_selector = self.config.get("item_selector", ".opportunity")
        title_selector = self.config.get("title_selector", "h3, h2, .title")
        link_selector = self.config.get("link_selector", "a")
        desc_selector = self.config.get("description_selector", "p, .description")
        funder = self.config.get("funder")
        base_url = self.config.get("base_url", "").rstrip("/")

        items = soup.select(item_selector)
        opportunities = []

        for item in items:
            title_el = item.select_one(title_selector)
            if not title_el:
                continue
            title = title_el.get_text(strip=True)

            link_el = item.select_one(link_selector)
            href = link_el.get("href", "") if link_el else ""
            if not href:
                continue
            if href.startswith("/") and base_url:
                href = base_url + href

            desc_el = item.select_one(desc_selector)
            description = desc_el.get_text(strip=True) if desc_el else ""

            keywords = extract_keywords(title)
            if description:
                keywords.extend(extract_keywords(description)[:10])
            keywords = list(dict.fromkeys(keywords))

            opp = ScrapedOpportunity(
                title=title,
                url=href,
                description=description,
                funder=funder,
                keywords=keywords,
                raw_html=str(item),
            )
            opportunities.append(opp)

        logger.info(f"Web scraper found {len(opportunities)} items from {self.source_url}")
        return opportunities
