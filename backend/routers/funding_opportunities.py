from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.crud import funding_opportunity as crud
from backend.db.session import get_db
from backend.schemas.funding_opportunity import OpportunityCreate, OpportunityOut, OpportunityList

router = APIRouter(prefix="/api/opportunities", tags=["opportunities"])


@router.post("", response_model=OpportunityOut, status_code=201)
async def create_opportunity(
    data: OpportunityCreate, db: AsyncSession = Depends(get_db)
):
    opp = await crud.create_opportunity(db, data)
    return opp


@router.get("", response_model=OpportunityList)
async def list_opportunities(
    page: int = 1,
    per_page: int = 20,
    funder: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    items, total = await crud.list_opportunities(
        db, page=page, per_page=per_page, funder=funder
    )
    return OpportunityList(items=items, total=total, page=page, per_page=per_page)


@router.get("/{opp_id}", response_model=OpportunityOut)
async def get_opportunity(opp_id: int, db: AsyncSession = Depends(get_db)):
    opp = await crud.get_opportunity(db, opp_id)
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return opp
