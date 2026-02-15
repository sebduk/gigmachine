"""Scraping orchestration — fetches from all due data sources."""
from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from backend.crud.data_source import list_due_sources
from backend.crud.funding_opportunity import create_opportunity, get_opportunity_by_url
from backend.models.data_source import DataSource
from backend.schemas.funding_opportunity import OpportunityCreate
from backend.services.matching import run_matching_for_opportunity
from backend.services.scraping.base import ScrapedOpportunity
from backend.services.scraping.registry import get_scraper

logger = logging.getLogger(__name__)


async def ingest_opportunity(
    db: AsyncSession, scraped: ScrapedOpportunity, source: DataSource
) -> int | None:
    """Ingest a single scraped opportunity. Returns the opportunity ID if new, None if duplicate."""
    existing = await get_opportunity_by_url(db, scraped.url)
    if existing:
        return None

    opp_data = OpportunityCreate(
        title=scraped.title,
        url=scraped.url,
        description=scraped.description,
        funder=scraped.funder or source.name,
        institution=scraped.institution,
        deadline=scraped.deadline,
        budget_min=scraped.budget_min,
        budget_max=scraped.budget_max,
        currency=scraped.currency,
        eligibility_criteria=scraped.eligibility_criteria,
        career_stages=scraped.career_stages,
        source_id=source.id,
        external_id=scraped.external_id,
        keyword_values=scraped.keywords,
        field_names=scraped.fields,
    )
    opp = await create_opportunity(db, opp_data)
    return opp.id


async def scrape_source(db: AsyncSession, source: DataSource) -> int:
    """Scrape a single data source and ingest results.

    Returns the number of new opportunities ingested.
    """
    try:
        scraper = get_scraper(
            source.parser_class_name,
            source.url,
            source.parser_config,
        )
        results = await scraper.scrape()

        new_count = 0
        for scraped in results:
            opp_id = await ingest_opportunity(db, scraped, source)
            if opp_id is not None:
                # Run matching for the new opportunity
                await run_matching_for_opportunity(db, opp_id)
                new_count += 1

        # Update source health
        source.last_scrape_status = "success"
        source.last_error_message = None
        source.consecutive_failures = 0
        await db.flush()

        logger.info(f"Source '{source.name}': {new_count} new from {len(results)} scraped")
        return new_count

    except Exception as e:
        source.last_scrape_status = "error"
        source.last_error_message = str(e)[:1000]
        source.consecutive_failures += 1
        await db.flush()

        logger.error(f"Source '{source.name}' failed: {e}")
        return 0


async def run_all_due_scrapes(db: AsyncSession) -> dict:
    """Scrape all sources that are due. Returns a summary."""
    sources = await list_due_sources(db)
    logger.info(f"Found {len(sources)} sources due for scraping")

    results = {}
    for source in sources:
        new_count = await scrape_source(db, source)
        results[source.name] = new_count

    return results
