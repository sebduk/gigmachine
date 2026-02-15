from __future__ import annotations

import enum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import String, Text, Enum as SAEnum, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import Base
from backend.db.mixins import TimestampMixin

if TYPE_CHECKING:
    from backend.models.funding_opportunity import FundingOpportunity


class SourceType(str, enum.Enum):
    WEB_SCRAPE = "web_scrape"
    RSS = "rss"
    API = "api"
    JOB_BOARD = "job_board"


class DataSource(TimestampMixin, Base):
    __tablename__ = "data_sources"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    url: Mapped[str] = mapped_column(String(2000), nullable=False)
    source_type: Mapped[SourceType] = mapped_column(
        SAEnum(SourceType, values_callable=lambda e: [x.value for x in e]),
        nullable=False,
    )

    # Scraping configuration
    scrape_frequency_minutes: Mapped[int] = mapped_column(
        Integer, default=1440, server_default="1440",
    )
    parser_class_name: Mapped[str] = mapped_column(String(200), nullable=False)
    parser_config: Mapped[Optional[str]] = mapped_column(Text, default=None)
    is_active: Mapped[bool] = mapped_column(default=True, server_default="1")

    # Health tracking
    last_scrape_status: Mapped[Optional[str]] = mapped_column(String(50), default=None)
    last_error_message: Mapped[Optional[str]] = mapped_column(Text, default=None)
    consecutive_failures: Mapped[int] = mapped_column(default=0, server_default="0")

    # Relationships
    opportunities: Mapped[List["FundingOpportunity"]] = relationship(back_populates="source")

    def __repr__(self) -> str:
        return f"<DataSource id={self.id} name={self.name!r} type={self.source_type.value}>"
