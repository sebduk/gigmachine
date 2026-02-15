from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.crud import match as crud
from backend.db.session import get_db
from backend.schemas.match import MatchOut, MatchAction, MatchList
from backend.services.matching import run_matching_for_profile

router = APIRouter(prefix="/api/profiles/{profile_id}/matches", tags=["matches"])


@router.get("", response_model=MatchList)
async def list_matches(
    profile_id: int,
    page: int = 1,
    per_page: int = 20,
    include_dismissed: bool = False,
    db: AsyncSession = Depends(get_db),
):
    items, total = await crud.get_matches_for_profile(
        db, profile_id, page=page, per_page=per_page,
        include_dismissed=include_dismissed,
    )
    return MatchList(items=items, total=total, page=page, per_page=per_page)


@router.post("/refresh", response_model=dict)
async def refresh_matches(profile_id: int, db: AsyncSession = Depends(get_db)):
    """Trigger re-matching for this profile against all active opportunities."""
    new_matches = await run_matching_for_profile(db, profile_id)
    return {"new_matches": new_matches}


@router.patch("/{match_id}", response_model=MatchOut)
async def update_match(
    profile_id: int,
    match_id: int,
    action: MatchAction,
    db: AsyncSession = Depends(get_db),
):
    match = await crud.get_match(db, match_id)
    if not match or match.profile_id != profile_id:
        raise HTTPException(status_code=404, detail="Match not found")
    updated = await crud.update_match_action(db, match, action)
    return updated
