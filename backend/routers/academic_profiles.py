from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.crud import academic_profile as crud
from backend.db.session import get_db
from backend.schemas.academic_profile import ProfileCreate, ProfileOut, ProfileUpdate

router = APIRouter(prefix="/api/profiles", tags=["profiles"])


@router.post("", response_model=ProfileOut, status_code=201)
async def create_profile(data: ProfileCreate, db: AsyncSession = Depends(get_db)):
    profile = await crud.create_profile(db, data)
    return profile


@router.get("", response_model=list[ProfileOut])
async def list_profiles(
    page: int = 1, per_page: int = 20, db: AsyncSession = Depends(get_db)
):
    profiles, _ = await crud.list_profiles(db, page=page, per_page=per_page)
    return profiles


@router.get("/{profile_id}", response_model=ProfileOut)
async def get_profile(profile_id: int, db: AsyncSession = Depends(get_db)):
    profile = await crud.get_profile(db, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.patch("/{profile_id}", response_model=ProfileOut)
async def update_profile(
    profile_id: int, data: ProfileUpdate, db: AsyncSession = Depends(get_db)
):
    profile = await crud.get_profile(db, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    updated = await crud.update_profile(db, profile, data)
    return updated


@router.delete("/{profile_id}", status_code=204)
async def delete_profile(profile_id: int, db: AsyncSession = Depends(get_db)):
    profile = await crud.get_profile(db, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    await crud.delete_profile(db, profile)
