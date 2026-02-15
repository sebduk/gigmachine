"""RSS/Atom feed scraper for funding opportunity feeds."""
from __future__ import annotations

import logging
from typing import List

import feedparser

from backend.services.scraping.base import BaseScraper, ScrapedOpportunity
from backend.utils.text import extract_keywords

logger = logging.getLogger(__name__)


class RssScraper(BaseScraper):
    """Scrape funding opportunities from RSS/Atom feeds.

    Parser config options:
        funder: str — override funder name for all entries
        keyword_tags: list[str] — feed tag names to extract keywords from
    """

    async def scrape(self) -> List[ScrapedOpportunity]:
        raw = await self.fetch()
        feed = feedparser.parse(raw)
        opportunities = []

        funder_override = self.config.get("funder")
        keyword_tags = self.config.get("keyword_tags", ["tags", "category"])

        for entry in feed.entries:
            # Extract keywords from tags/categories
            keywords = []
            for tag_field in keyword_tags:
                tags = getattr(entry, tag_field, None)
                if tags and isinstance(tags, list):
                    for tag in tags:
                        term = tag.get("term", "") if isinstance(tag, dict) else str(tag)
                        if term:
                            keywords.append(term.lower())

            # Also extract keywords from title
            title_keywords = extract_keywords(entry.get("title", ""))
            keywords.extend(title_keywords)

            # Deduplicate
            keywords = list(dict.fromkeys(keywords))

            link = entry.get("link", "")
            if not link:
                continue

            opp = ScrapedOpportunity(
                title=entry.get("title", "Untitled"),
                url=link,
                description=entry.get("summary", entry.get("description", "")),
                funder=funder_override,
                external_id=entry.get("id", link),
                keywords=keywords,
                raw_html=entry.get("summary", ""),
            )
            opportunities.append(opp)

        logger.info(f"RSS scraper found {len(opportunities)} opportunities from {self.source_url}")
        return opportunities
