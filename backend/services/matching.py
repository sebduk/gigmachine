"""
Matching engine — connects academic profiles with funding opportunities.

Phase 1: Keyword & field overlap matching
Phase 2 (future): Semantic embedding similarity using LLM

The matching score is a weighted combination of:
  - keyword_overlap: How many keywords match (Jaccard similarity)
  - field_overlap: How many research fields match
  - career_stage_match: Whether the profile's career stage is eligible
  - deadline_proximity: Bonus for upcoming (but not expired) deadlines
"""
from __future__ import annotations

import json
import logging
from datetime import date
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.crud.match import create_match, match_exists
from backend.models import Keyword, ResearchField
from backend.models.academic_profile import AcademicProfile
from backend.models.funding_opportunity import FundingOpportunity

logger = logging.getLogger(__name__)

# Weights for scoring components
WEIGHT_KEYWORD = 0.40
WEIGHT_FIELD = 0.35
WEIGHT_CAREER = 0.15
WEIGHT_DEADLINE = 0.10

# Minimum score to create a match
MIN_MATCH_SCORE = 0.1


def _jaccard(set_a: set, set_b: set) -> float:
    """Jaccard similarity: |A ∩ B| / |A ∪ B|"""
    if not set_a and not set_b:
        return 0.0
    intersection = set_a & set_b
    union = set_a | set_b
    return len(intersection) / len(union) if union else 0.0


def _keyword_score(profile_keywords: set[str], opp_keywords: set[str]) -> tuple[float, list[str]]:
    """Score based on keyword overlap."""
    overlap = profile_keywords & opp_keywords
    score = _jaccard(profile_keywords, opp_keywords)
    return score, sorted(overlap)


def _field_score(profile_fields: set[str], opp_fields: set[str]) -> tuple[float, list[str]]:
    """Score based on research field overlap."""
    overlap = profile_fields & opp_fields
    score = _jaccard(profile_fields, opp_fields)
    return score, sorted(overlap)


def _career_stage_score(profile_stage: str | None, opp_stages: str | None) -> tuple[float, str]:
    """Score based on career stage eligibility."""
    if not profile_stage or not opp_stages:
        # No restriction specified — assume eligible
        return 1.0, "no_restriction"
    eligible = {s.strip().lower() for s in opp_stages.split(",")}
    if profile_stage.lower() in eligible:
        return 1.0, "eligible"
    return 0.0, "ineligible"


def _deadline_score(deadline: date | None) -> tuple[float, str]:
    """Bonus for opportunities with upcoming deadlines."""
    if not deadline:
        return 0.5, "no_deadline"
    today = date.today()
    if deadline < today:
        return 0.0, "expired"
    days_until = (deadline - today).days
    if days_until <= 30:
        return 1.0, f"{days_until}d_urgent"
    elif days_until <= 90:
        return 0.7, f"{days_until}d_upcoming"
    else:
        return 0.4, f"{days_until}d_future"


def compute_match_score(
    profile: AcademicProfile,
    opportunity: FundingOpportunity,
) -> tuple[float, str]:
    """Compute a match score between a profile and an opportunity.

    Returns (score, reasons_json).
    """
    profile_kw = {kw.value.lower() for kw in profile.keywords}
    opp_kw = {kw.value.lower() for kw in opportunity.keywords}
    kw_score, kw_overlap = _keyword_score(profile_kw, opp_kw)

    profile_f = {f.name.lower() for f in profile.fields}
    opp_f = {f.name.lower() for f in opportunity.fields}
    f_score, f_overlap = _field_score(profile_f, opp_f)

    career_val = profile.career_stage.value if profile.career_stage else None
    c_score, c_reason = _career_stage_score(career_val, opportunity.career_stages)
    d_score, d_reason = _deadline_score(opportunity.deadline)

    total = (
        WEIGHT_KEYWORD * kw_score
        + WEIGHT_FIELD * f_score
        + WEIGHT_CAREER * c_score
        + WEIGHT_DEADLINE * d_score
    )

    reasons = [
        {"type": "keyword_overlap", "detail": kw_overlap, "score": round(kw_score, 3), "weight": WEIGHT_KEYWORD},
        {"type": "field_overlap", "detail": f_overlap, "score": round(f_score, 3), "weight": WEIGHT_FIELD},
        {"type": "career_stage", "detail": c_reason, "score": round(c_score, 3), "weight": WEIGHT_CAREER},
        {"type": "deadline", "detail": d_reason, "score": round(d_score, 3), "weight": WEIGHT_DEADLINE},
    ]

    return round(total, 4), json.dumps(reasons)


async def run_matching_for_profile(
    db: AsyncSession, profile_id: int
) -> int:
    """Run matching for a single profile against all active opportunities.

    Returns the number of new matches created.
    """
    # Load profile with keywords and fields
    result = await db.execute(
        select(AcademicProfile)
        .options(selectinload(AcademicProfile.keywords), selectinload(AcademicProfile.fields))
        .where(AcademicProfile.id == profile_id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        logger.warning(f"Profile {profile_id} not found for matching")
        return 0

    # Load all active opportunities
    opp_result = await db.execute(
        select(FundingOpportunity)
        .options(
            selectinload(FundingOpportunity.keywords),
            selectinload(FundingOpportunity.fields),
        )
        .where(FundingOpportunity.deleted_at.is_(None))
    )
    opportunities = opp_result.scalars().all()

    new_count = 0
    for opp in opportunities:
        # Skip if already matched
        if await match_exists(db, profile.id, opp.id):
            continue

        score, reasons = compute_match_score(profile, opp)
        if score >= MIN_MATCH_SCORE:
            await create_match(
                db,
                profile_id=profile.id,
                opportunity_id=opp.id,
                score=score,
                match_method="keyword",
                match_reasons=reasons,
            )
            new_count += 1

    logger.info(f"Matching for profile {profile_id}: {new_count} new matches from {len(opportunities)} opportunities")
    return new_count


async def run_matching_for_opportunity(
    db: AsyncSession, opportunity_id: int
) -> int:
    """Run matching for a new opportunity against all profiles.

    Called after a scraper ingests a new opportunity.
    Returns the number of new matches created.
    """
    opp_result = await db.execute(
        select(FundingOpportunity)
        .options(
            selectinload(FundingOpportunity.keywords),
            selectinload(FundingOpportunity.fields),
        )
        .where(FundingOpportunity.id == opportunity_id)
    )
    opp = opp_result.scalar_one_or_none()
    if not opp:
        return 0

    profile_result = await db.execute(
        select(AcademicProfile)
        .options(
            selectinload(AcademicProfile.keywords),
            selectinload(AcademicProfile.fields),
        )
    )
    profiles = profile_result.scalars().all()

    new_count = 0
    for profile in profiles:
        if await match_exists(db, profile.id, opp.id):
            continue

        score, reasons = compute_match_score(profile, opp)
        if score >= profile.match_threshold:
            await create_match(
                db,
                profile_id=profile.id,
                opportunity_id=opp.id,
                score=score,
                match_method="keyword",
                match_reasons=reasons,
            )
            new_count += 1

    logger.info(f"Matching for opportunity {opportunity_id}: {new_count} new matches from {len(profiles)} profiles")
    return new_count
