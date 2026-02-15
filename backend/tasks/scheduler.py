"""Background task scheduler using APScheduler."""
from __future__ import annotations

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from backend.db.session import async_session_factory
from backend.tasks.scrape_jobs import run_all_due_scrapes

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def _scheduled_scrape():
    """Wrapper that creates a DB session for the scheduled scrape job."""
    async with async_session_factory() as db:
        try:
            results = await run_all_due_scrapes(db)
            await db.commit()
            total = sum(results.values())
            logger.info(f"Scheduled scrape complete: {total} new opportunities")
        except Exception as e:
            await db.rollback()
            logger.error(f"Scheduled scrape failed: {e}")


def start_scheduler():
    """Start the background scheduler with default jobs."""
    # Check for due scrapes every 15 minutes
    scheduler.add_job(
        _scheduled_scrape,
        "interval",
        minutes=15,
        id="scrape_all_due",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Background scheduler started")


def stop_scheduler():
    """Stop the background scheduler."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Background scheduler stopped")
