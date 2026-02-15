from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field

from backend.models.academic_profile import CareerStage


class KeywordOut(BaseModel):
    id: int
    value: str

    model_config = {"from_attributes": True}


class ResearchFieldOut(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class ProfileCreate(BaseModel):
    name: str = Field(max_length=300)
    email: str = Field(max_length=320)
    career_stage: Optional[CareerStage] = None
    institution: Optional[str] = Field(default=None, max_length=300)
    department: Optional[str] = Field(default=None, max_length=300)
    bio: Optional[str] = None
    publications_summary: Optional[str] = None
    orcid: Optional[str] = Field(default=None, max_length=19)
    keyword_values: List[str] = Field(default_factory=list)
    field_names: List[str] = Field(default_factory=list)
    match_threshold: float = Field(default=0.5, ge=0.0, le=1.0)


class ProfileUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=300)
    career_stage: Optional[CareerStage] = None
    institution: Optional[str] = Field(default=None, max_length=300)
    department: Optional[str] = Field(default=None, max_length=300)
    bio: Optional[str] = None
    publications_summary: Optional[str] = None
    orcid: Optional[str] = Field(default=None, max_length=19)
    keyword_values: Optional[List[str]] = None
    field_names: Optional[List[str]] = None
    match_threshold: Optional[float] = Field(default=None, ge=0.0, le=1.0)


class ProfileOut(BaseModel):
    id: int
    name: str
    email: str
    career_stage: Optional[CareerStage] = None
    institution: Optional[str] = None
    department: Optional[str] = None
    bio: Optional[str] = None
    publications_summary: Optional[str] = None
    orcid: Optional[str] = None
    match_threshold: float
    keywords: List[KeywordOut] = []
    fields: List[ResearchFieldOut] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
