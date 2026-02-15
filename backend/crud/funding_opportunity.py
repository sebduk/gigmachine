from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.crud.academic_profile import _get_or_create_keywords, _get_or_create_fields
from backend.models.funding_opportunity import FundingOpportunity
from backend.schemas.funding_opportunity import OpportunityCreate


async def create_opportunity(
    db: AsyncSession, data: OpportunityCreate
) -> FundingOpportunity:
    opp = FundingOpportunity(
        title=data.title,
        description=data.description,
        funder=data.funder,
        institution=data.institution,
        deadline=data.deadline,
        budget_min=data.budget_min,
        budget_max=data.budget_max,
        currency=data.currency,
        eligibility_criteria=data.eligibility_criteria,
        career_stages=data.career_stages,
        url=data.url,
        source_id=data.source_id,
        external_id=data.external_id,
    )
    opp.keywords = await _get_or_create_keywords(db, data.keyword_values)
    opp.fields = await _get_or_create_fields(db, data.field_names)
    db.add(opp)
    await db.flush()
    return opp


async def get_opportunity(
    db: AsyncSession, opp_id: int
) -> Optional[FundingOpportunity]:
    result = await db.execute(
        select(FundingOpportunity)
        .options(
            selectinload(FundingOpportunity.keywords),
            selectinload(FundingOpportunity.fields),
        )
        .where(FundingOpportunity.id == opp_id)
        .where(FundingOpportunity.deleted_at.is_(None))
    )
    return result.scalar_one_or_none()


async def list_opportunities(
    db: AsyncSession,
    page: int = 1,
    per_page: int = 20,
    funder: Optional[str] = None,
) -> tuple[List[FundingOpportunity], int]:
    base = select(FundingOpportunity).where(FundingOpportunity.deleted_at.is_(None))
    if funder:
        base = base.where(FundingOpportunity.funder.ilike(f"%{funder}%"))

    count_q = select(func.count()).select_from(base.subquery())
    count_result = await db.execute(count_q)
    total = count_result.scalar_one()

    offset = (page - 1) * per_page
    result = await db.execute(
        base.options(
            selectinload(FundingOpportunity.keywords),
            selectinload(FundingOpportunity.fields),
        )
        .order_by(FundingOpportunity.deadline.asc().nullslast())
        .offset(offset)
        .limit(per_page)
    )
    return result.scalars().all(), total


async def get_opportunity_by_url(
    db: AsyncSession, url: str
) -> Optional[FundingOpportunity]:
    result = await db.execute(
        select(FundingOpportunity).where(FundingOpportunity.url == url)
    )
    return result.scalar_one_or_none()
