from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

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
    """Create a new profile. Only handle + email required. No real names."""
    handle: str = Field(max_length=100, description="Your pseudonym — not your real name")
    email: str = Field(max_length=320, description="For notifications only, never shared")
    career_stage: Optional[CareerStage] = None
    research_summary: Optional[str] = Field(
        default=None,
        description="Describe your research interests. Avoid including personal details.",
    )
    keyword_values: List[str] = Field(default_factory=list)
    field_names: List[str] = Field(default_factory=list)
    match_threshold: float = Field(default=0.5, ge=0.0, le=1.0)


class ProfileUpdate(BaseModel):
    handle: Optional[str] = Field(default=None, max_length=100)
    career_stage: Optional[CareerStage] = None
    research_summary: Optional[str] = None
    keyword_values: Optional[List[str]] = None
    field_names: Optional[List[str]] = None
    match_threshold: Optional[float] = Field(default=None, ge=0.0, le=1.0)


class ProfileOut(BaseModel):
    """Public profile response. Note: email is intentionally excluded."""
    id: int
    handle: str
    career_stage: Optional[CareerStage] = None
    research_summary: Optional[str] = None
    match_threshold: float
    keywords: List[KeywordOut] = []
    fields: List[ResearchFieldOut] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProfilePrivateOut(ProfileOut):
    """Private profile response — includes email. Only returned to the profile owner."""
    email: str


class ResearchIndexOut(BaseModel):
    id: int
    source_type: str
    extracted_topics: Optional[str] = None
    extracted_methods: Optional[str] = None
    extracted_domains: Optional[str] = None
    work_type: Optional[str] = None
    experience_years: Optional[int] = None
    summary: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentUpload(BaseModel):
    """Upload a document (CV, publication list) for research indexing.
    The raw text is processed to extract research topics, then discarded."""
    source_type: str = Field(description="cv, publication, grant_history")
    raw_text: str = Field(description="Document text content. PII will be stripped before storage.")


class PiiWarning(BaseModel):
    """Returned when PII is detected in user-submitted text."""
    warnings: List[str]
    field_name: str
