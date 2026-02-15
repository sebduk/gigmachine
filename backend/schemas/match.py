from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from backend.schemas.funding_opportunity import OpportunityOut


class MatchOut(BaseModel):
    id: int
    profile_id: int
    opportunity_id: int
    score: float
    match_method: str
    match_reasons: Optional[str] = None
    is_seen: bool
    is_saved: bool
    is_dismissed: bool
    opportunity: OpportunityOut
    created_at: datetime

    model_config = {"from_attributes": True}


class MatchAction(BaseModel):
    """For marking a match as seen/saved/dismissed."""
    is_seen: Optional[bool] = None
    is_saved: Optional[bool] = None
    is_dismissed: Optional[bool] = None


class MatchList(BaseModel):
    items: list[MatchOut]
    total: int
    page: int
    per_page: int
