from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.data_source import DataSource
from backend.schemas.data_source import DataSourceCreate, DataSourceUpdate


async def create_data_source(db: AsyncSession, data: DataSourceCreate) -> DataSource:
    source = DataSource(**data.model_dump())
    db.add(source)
    await db.flush()
    return source


async def get_data_source(db: AsyncSession, source_id: int) -> Optional[DataSource]:
    result = await db.execute(select(DataSource).where(DataSource.id == source_id))
    return result.scalar_one_or_none()


async def list_data_sources(
    db: AsyncSession, active_only: bool = False
) -> List[DataSource]:
    query = select(DataSource)
    if active_only:
        query = query.where(DataSource.is_active.is_(True))
    result = await db.execute(query.order_by(DataSource.name))
    return result.scalars().all()


async def update_data_source(
    db: AsyncSession, source: DataSource, data: DataSourceUpdate
) -> DataSource:
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(source, key, value)
    await db.flush()
    return source


async def list_due_sources(db: AsyncSession) -> List[DataSource]:
    """Get active sources that are due for scraping.
    A source is due when NOW - last_updated >= scrape_frequency_minutes.
    """
    from sqlalchemy import text
    result = await db.execute(
        select(DataSource)
        .where(DataSource.is_active.is_(True))
        .where(
            text(
                "TIMESTAMPDIFF(MINUTE, data_sources.updated_at, NOW()) >= "
                "data_sources.scrape_frequency_minutes"
            )
        )
    )
    return result.scalars().all()
