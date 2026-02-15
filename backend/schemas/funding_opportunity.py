from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field

from backend.schemas.academic_profile import KeywordOut, ResearchFieldOut


class OpportunityCreate(BaseModel):
    title: str = Field(max_length=500)
    description: Optional[str] = None
    funder: Optional[str] = Field(default=None, max_length=300)
    institution: Optional[str] = Field(default=None, max_length=300)
    deadline: Optional[date] = None
    budget_min: Optional[Decimal] = None
    budget_max: Optional[Decimal] = None
    currency: str = Field(default="USD", max_length=3)
    eligibility_criteria: Optional[str] = None
    career_stages: Optional[str] = None
    url: str = Field(max_length=2000)
    source_id: Optional[int] = None
    external_id: Optional[str] = None
    keyword_values: List[str] = Field(default_factory=list)
    field_names: List[str] = Field(default_factory=list)


class OpportunityOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    funder: Optional[str] = None
    institution: Optional[str] = None
    deadline: Optional[date] = None
    budget_min: Optional[Decimal] = None
    budget_max: Optional[Decimal] = None
    currency: str
    eligibility_criteria: Optional[str] = None
    career_stages: Optional[str] = None
    url: str
    source_id: Optional[int] = None
    external_id: Optional[str] = None
    keywords: List[KeywordOut] = []
    fields: List[ResearchFieldOut] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class OpportunityList(BaseModel):
    items: List[OpportunityOut]
    total: int
    page: int
    per_page: int
