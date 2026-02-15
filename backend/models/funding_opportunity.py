from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import String, Text, Numeric, Date, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import Base
from backend.db.mixins import TimestampMixin, SoftDeleteMixin
from backend.models.associations import opportunity_keyword, opportunity_field

if TYPE_CHECKING:
    from backend.models.data_source import DataSource
    from backend.models.match import Match


class FundingOpportunity(TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "funding_opportunities"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Core fields
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, default=None)
    funder: Mapped[Optional[str]] = mapped_column(String(300), default=None)
    institution: Mapped[Optional[str]] = mapped_column(String(300), default=None)

    # Dates and money
    deadline: Mapped[Optional[date]] = mapped_column(Date, default=None, index=True)
    budget_min: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2), default=None)
    budget_max: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2), default=None)
    currency: Mapped[str] = mapped_column(String(3), default="USD", server_default="USD")

    # Eligibility
    eligibility_criteria: Mapped[Optional[str]] = mapped_column(Text, default=None)
    career_stages: Mapped[Optional[str]] = mapped_column(String(200), default=None)

    # Source tracking
    url: Mapped[str] = mapped_column(String(2000), nullable=False, unique=True)
    source_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("data_sources.id", ondelete="SET NULL"), default=None,
    )
    external_id: Mapped[Optional[str]] = mapped_column(String(500), default=None)
    raw_html: Mapped[Optional[str]] = mapped_column(Text, default=None)

    # Relationships
    source: Mapped[Optional["DataSource"]] = relationship(back_populates="opportunities")
    keywords: Mapped[List["Keyword"]] = relationship(
        secondary=opportunity_keyword, back_populates="opportunities", lazy="selectin",
    )
    fields: Mapped[List["ResearchField"]] = relationship(
        secondary=opportunity_field, back_populates="opportunities", lazy="selectin",
    )
    matches: Mapped[List["Match"]] = relationship(back_populates="opportunity")

    __table_args__ = (
        Index("ix_opp_funder", "funder"),
        Index("ix_opp_source_external", "source_id", "external_id", unique=True),
    )

    def __repr__(self) -> str:
        return f"<FundingOpportunity id={self.id} title={self.title!r}>"


from backend.models import Keyword, ResearchField  # noqa: E402, F401
