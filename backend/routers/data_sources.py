from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.crud import data_source as crud
from backend.db.session import get_db
from backend.schemas.data_source import DataSourceCreate, DataSourceOut, DataSourceUpdate

router = APIRouter(prefix="/api/sources", tags=["sources"])


@router.post("", response_model=DataSourceOut, status_code=201)
async def create_source(data: DataSourceCreate, db: AsyncSession = Depends(get_db)):
    source = await crud.create_data_source(db, data)
    return source


@router.get("", response_model=list[DataSourceOut])
async def list_sources(
    active_only: bool = False, db: AsyncSession = Depends(get_db)
):
    return await crud.list_data_sources(db, active_only=active_only)


@router.get("/{source_id}", response_model=DataSourceOut)
async def get_source(source_id: int, db: AsyncSession = Depends(get_db)):
    source = await crud.get_data_source(db, source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Data source not found")
    return source


@router.patch("/{source_id}", response_model=DataSourceOut)
async def update_source(
    source_id: int, data: DataSourceUpdate, db: AsyncSession = Depends(get_db)
):
    source = await crud.get_data_source(db, source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Data source not found")
    updated = await crud.update_data_source(db, source, data)
    return updated
