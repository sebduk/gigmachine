from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from backend.models.data_source import SourceType


class DataSourceCreate(BaseModel):
    name: str = Field(max_length=200)
    url: str = Field(max_length=2000)
    source_type: SourceType
    scrape_frequency_minutes: int = Field(default=1440, ge=5)
    parser_class_name: str = Field(max_length=200)
    parser_config: Optional[str] = None
    is_active: bool = True


class DataSourceUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=200)
    url: Optional[str] = Field(default=None, max_length=2000)
    scrape_frequency_minutes: Optional[int] = Field(default=None, ge=5)
    parser_config: Optional[str] = None
    is_active: Optional[bool] = None


class DataSourceOut(BaseModel):
    id: int
    name: str
    url: str
    source_type: SourceType
    scrape_frequency_minutes: int
    parser_class_name: str
    parser_config: Optional[str] = None
    is_active: bool
    last_scrape_status: Optional[str] = None
    last_error_message: Optional[str] = None
    consecutive_failures: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
