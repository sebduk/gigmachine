import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.crud import academic_profile as crud
from backend.db.session import get_db
from backend.models.research_index import ResearchIndex
from backend.schemas.academic_profile import (
    DocumentUpload,
    PiiWarning,
    ProfileCreate,
    ProfileOut,
    ProfilePrivateOut,
    ProfileUpdate,
    ResearchIndexOut,
)
from backend.utils.privacy import strip_pii, validate_no_pii

router = APIRouter(prefix="/api/profiles", tags=["profiles"])


@router.post("", response_model=ProfilePrivateOut, status_code=201)
async def create_profile(data: ProfileCreate, db: AsyncSession = Depends(get_db)):
    """Create a new pseudonymous profile. Only handle + email required."""
    # Warn if research_summary contains PII
    pii_warnings = []
    if data.research_summary:
        warnings = validate_no_pii(data.research_summary)
        if warnings:
            pii_warnings.extend(warnings)
    if pii_warnings:
        raise HTTPException(
            status_code=422,
            detail={"pii_warnings": pii_warnings,
                    "message": "Your research summary appears to contain personal information. "
                               "Please remove it and try again."},
        )
    profile = await crud.create_profile(db, data)
    return profile


@router.get("", response_model=list[ProfileOut])
async def list_profiles(
    page: int = 1, per_page: int = 20, db: AsyncSession = Depends(get_db)
):
    """List profiles. Email is excluded from public responses."""
    profiles, _ = await crud.list_profiles(db, page=page, per_page=per_page)
    return profiles


@router.get("/{profile_id}", response_model=ProfileOut)
async def get_profile(profile_id: int, db: AsyncSession = Depends(get_db)):
    """Get a profile. Email excluded — use /me endpoint for private data."""
    profile = await crud.get_profile(db, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.get("/{profile_id}/private", response_model=ProfilePrivateOut)
async def get_profile_private(profile_id: int, db: AsyncSession = Depends(get_db)):
    """Get full profile including email. Only for the profile owner (auth TBD)."""
    profile = await crud.get_profile(db, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.patch("/{profile_id}", response_model=ProfileOut)
async def update_profile(
    profile_id: int, data: ProfileUpdate, db: AsyncSession = Depends(get_db)
):
    if data.research_summary:
        warnings = validate_no_pii(data.research_summary)
        if warnings:
            raise HTTPException(
                status_code=422,
                detail={"pii_warnings": warnings,
                        "message": "Your research summary appears to contain personal information."},
            )
    profile = await crud.get_profile(db, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    updated = await crud.update_profile(db, profile, data)
    return updated


@router.delete("/{profile_id}", status_code=204)
async def delete_profile(profile_id: int, db: AsyncSession = Depends(get_db)):
    """Right to erasure: permanently delete profile and all associated data.
    This cascades to matches, research index entries, and keyword associations."""
    profile = await crud.get_profile(db, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    await crud.delete_profile(db, profile)


@router.post("/{profile_id}/research", response_model=ResearchIndexOut, status_code=201)
async def upload_document(
    profile_id: int, data: DocumentUpload, db: AsyncSession = Depends(get_db)
):
    """Upload a document for research indexing.

    The raw text is run through PII stripping, then we extract research
    topics and methodologies. The original document is never stored —
    only the anonymized research fingerprint is kept.
    """
    profile = await crud.get_profile(db, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Strip PII from the document
    stripped = strip_pii(data.raw_text)

    # Extract research content from cleaned text
    # For now, use the cleaned text as the summary and extract keywords.
    # Future: use LLM to extract structured topics/methods/domains.
    from backend.utils.text import extract_keywords
    topics = extract_keywords(stripped.clean_text)

    entry = ResearchIndex(
        profile_id=profile_id,
        source_type=data.source_type,
        extracted_topics=json.dumps(topics[:50]),  # cap at 50
        summary=stripped.clean_text[:2000] if stripped.clean_text else None,
        source_hash=stripped.source_hash,
    )
    db.add(entry)
    await db.flush()
    return entry


@router.get("/{profile_id}/research", response_model=list[ResearchIndexOut])
async def list_research_entries(
    profile_id: int, db: AsyncSession = Depends(get_db)
):
    """List all research index entries for a profile."""
    profile = await crud.get_profile(db, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile.research_entries


@router.get("/{profile_id}/data-export", response_model=dict)
async def export_profile_data(profile_id: int, db: AsyncSession = Depends(get_db)):
    """Right to access: export all data we hold about this profile."""
    profile = await crud.get_profile(db, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return {
        "profile": {
            "handle": profile.handle,
            "email": profile.email,
            "career_stage": profile.career_stage.value if profile.career_stage else None,
            "research_summary": profile.research_summary,
            "keywords": [kw.value for kw in profile.keywords],
            "fields": [f.name for f in profile.fields],
            "match_threshold": profile.match_threshold,
            "created_at": profile.created_at.isoformat(),
        },
        "research_entries": [
            {
                "source_type": r.source_type,
                "extracted_topics": r.extracted_topics,
                "summary": r.summary,
                "created_at": r.created_at.isoformat(),
            }
            for r in profile.research_entries
        ],
        "match_count": len(profile.matches),
        "_privacy_note": "This is all data we hold about you. "
                         "Use DELETE /api/profiles/{id} to permanently erase everything.",
    }
