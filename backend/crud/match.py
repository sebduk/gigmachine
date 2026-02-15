from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.models.match import Match
from backend.models.funding_opportunity import FundingOpportunity
from backend.schemas.match import MatchAction


async def create_match(
    db: AsyncSession,
    profile_id: int,
    opportunity_id: int,
    score: float,
    match_method: str = "keyword",
    match_reasons: Optional[str] = None,
) -> Match:
    match = Match(
        profile_id=profile_id,
        opportunity_id=opportunity_id,
        score=score,
        match_method=match_method,
        match_reasons=match_reasons,
    )
    db.add(match)
    await db.flush()
    return match


async def get_matches_for_profile(
    db: AsyncSession,
    profile_id: int,
    page: int = 1,
    per_page: int = 20,
    include_dismissed: bool = False,
) -> tuple[List[Match], int]:
    base = (
        select(Match)
        .where(Match.profile_id == profile_id)
    )
    if not include_dismissed:
        base = base.where(Match.is_dismissed.is_(False))

    count_q = select(func.count()).select_from(base.subquery())
    count_result = await db.execute(count_q)
    total = count_result.scalar_one()

    offset = (page - 1) * per_page
    result = await db.execute(
        base.options(
            selectinload(Match.opportunity).selectinload(FundingOpportunity.keywords),
            selectinload(Match.opportunity).selectinload(FundingOpportunity.fields),
        )
        .order_by(Match.score.desc())
        .offset(offset)
        .limit(per_page)
    )
    return result.scalars().all(), total


async def update_match_action(
    db: AsyncSession, match: Match, action: MatchAction
) -> Match:
    update_data = action.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            setattr(match, key, value)
    await db.flush()
    return match


async def get_match(db: AsyncSession, match_id: int) -> Optional[Match]:
    result = await db.execute(
        select(Match)
        .options(
            selectinload(Match.opportunity).selectinload(FundingOpportunity.keywords),
            selectinload(Match.opportunity).selectinload(FundingOpportunity.fields),
        )
        .where(Match.id == match_id)
    )
    return result.scalar_one_or_none()


async def match_exists(
    db: AsyncSession, profile_id: int, opportunity_id: int
) -> bool:
    result = await db.execute(
        select(func.count(Match.id))
        .where(Match.profile_id == profile_id)
        .where(Match.opportunity_id == opportunity_id)
    )
    return result.scalar_one() > 0
