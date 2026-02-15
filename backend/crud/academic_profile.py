from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.models import Keyword, ResearchField
from backend.models.academic_profile import AcademicProfile
from backend.schemas.academic_profile import ProfileCreate, ProfileUpdate
from backend.utils.text import normalize_keyword


async def _get_or_create_keywords(db: AsyncSession, values: List[str]) -> List[Keyword]:
    """Get existing keywords or create new ones."""
    if not values:
        return []
    normalized = [normalize_keyword(v) for v in values if v.strip()]
    result = await db.execute(select(Keyword).where(Keyword.value.in_(normalized)))
    existing = {kw.value: kw for kw in result.scalars().all()}
    keywords = []
    for v in normalized:
        if v in existing:
            keywords.append(existing[v])
        else:
            kw = Keyword(value=v)
            db.add(kw)
            keywords.append(kw)
    return keywords


async def _get_or_create_fields(db: AsyncSession, names: List[str]) -> List[ResearchField]:
    """Get existing research fields or create new ones."""
    if not names:
        return []
    normalized = [n.strip() for n in names if n.strip()]
    result = await db.execute(select(ResearchField).where(ResearchField.name.in_(normalized)))
    existing = {f.name: f for f in result.scalars().all()}
    fields = []
    for n in normalized:
        if n in existing:
            fields.append(existing[n])
        else:
            field = ResearchField(name=n)
            db.add(field)
            fields.append(field)
    return fields


async def create_profile(db: AsyncSession, data: ProfileCreate) -> AcademicProfile:
    profile = AcademicProfile(
        handle=data.handle,
        email=data.email,
        career_stage=data.career_stage,
        research_summary=data.research_summary,
        match_threshold=data.match_threshold,
    )
    profile.keywords = await _get_or_create_keywords(db, data.keyword_values)
    profile.fields = await _get_or_create_fields(db, data.field_names)
    db.add(profile)
    await db.flush()
    return profile


async def get_profile(db: AsyncSession, profile_id: int) -> Optional[AcademicProfile]:
    result = await db.execute(
        select(AcademicProfile)
        .options(selectinload(AcademicProfile.keywords), selectinload(AcademicProfile.fields))
        .where(AcademicProfile.id == profile_id)
    )
    return result.scalar_one_or_none()


async def list_profiles(
    db: AsyncSession, page: int = 1, per_page: int = 20
) -> tuple[List[AcademicProfile], int]:
    offset = (page - 1) * per_page
    count_result = await db.execute(select(func.count(AcademicProfile.id)))
    total = count_result.scalar_one()
    result = await db.execute(
        select(AcademicProfile)
        .options(selectinload(AcademicProfile.keywords), selectinload(AcademicProfile.fields))
        .offset(offset)
        .limit(per_page)
    )
    return result.scalars().all(), total


async def update_profile(
    db: AsyncSession, profile: AcademicProfile, data: ProfileUpdate
) -> AcademicProfile:
    for field_name in ["handle", "career_stage", "research_summary", "match_threshold"]:
        value = getattr(data, field_name, None)
        if value is not None:
            setattr(profile, field_name, value)
    if data.keyword_values is not None:
        profile.keywords = await _get_or_create_keywords(db, data.keyword_values)
    if data.field_names is not None:
        profile.fields = await _get_or_create_fields(db, data.field_names)
    await db.flush()
    return profile


async def delete_profile(db: AsyncSession, profile: AcademicProfile) -> None:
    await db.delete(profile)
    await db.flush()
