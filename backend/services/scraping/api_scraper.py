"""API-based scraper for structured data sources (JSON APIs)."""
from __future__ import annotations

import json
import logging
from typing import Any, Dict, List

import httpx

from backend.config import settings
from backend.services.scraping.base import BaseScraper, ScrapedOpportunity

logger = logging.getLogger(__name__)


class ApiScraper(BaseScraper):
    """Scrape from JSON APIs that return structured funding data.

    Parser config (JSON):
        method: str — HTTP method (GET/POST), default GET
        headers: dict — additional headers
        params: dict — query parameters
        body: dict — request body (for POST)
        results_path: str — dot-notation path to results array (e.g., "data.results")
        field_map: dict — mapping from API field names to ScrapedOpportunity fields
            e.g., {"opportunityTitle": "title", "synopsis.synopsisDetail": "description"}
        funder: str — override funder name
    """

    async def scrape(self) -> List[ScrapedOpportunity]:
        method = self.config.get("method", "GET").upper()
        headers = {"User-Agent": settings.scrape_user_agent}
        headers.update(self.config.get("headers", {}))
        params = self.config.get("params", {})
        body = self.config.get("body")

        async with httpx.AsyncClient(
            headers=headers, follow_redirects=True, timeout=30.0
        ) as client:
            if method == "POST":
                response = await client.post(
                    self.source_url, params=params, json=body
                )
            else:
                response = await client.get(self.source_url, params=params)
            response.raise_for_status()
            data = response.json()

        # Navigate to results array using dot notation
        results_path = self.config.get("results_path", "")
        results = data
        if results_path:
            for key in results_path.split("."):
                if isinstance(results, dict):
                    results = results.get(key, [])
                else:
                    results = []
                    break

        if not isinstance(results, list):
            results = [results]

        field_map = self.config.get("field_map", {})
        funder = self.config.get("funder")
        opportunities = []

        for item in results:
            mapped = self._map_fields(item, field_map)
            title = mapped.get("title", "")
            url = mapped.get("url", "")
            if not title or not url:
                continue

            opp = ScrapedOpportunity(
                title=title,
                url=url,
                description=mapped.get("description"),
                funder=funder or mapped.get("funder"),
                external_id=mapped.get("external_id"),
                keywords=mapped.get("keywords", []),
            )
            opportunities.append(opp)

        logger.info(f"API scraper found {len(opportunities)} items from {self.source_url}")
        return opportunities

    @staticmethod
    def _map_fields(item: Dict[str, Any], field_map: Dict[str, str]) -> Dict[str, Any]:
        """Map API fields to our standard field names using dot notation."""
        result: Dict[str, Any] = {}
        for source_path, target_field in field_map.items():
            value = item
            for key in source_path.split("."):
                if isinstance(value, dict):
                    value = value.get(key)
                else:
                    value = None
                    break
            if value is not None:
                result[target_field] = value
        return result
