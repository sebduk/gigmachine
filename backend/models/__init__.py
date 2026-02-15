"""
Central registry of all models.
Alembic's env.py imports from here to discover all tables via Base.metadata.
Also defines the shared taxonomy tables: Keyword and ResearchField.
"""
from typing import List

from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import Base
from backend.models.associations import (
    profile_keyword,
    opportunity_keyword,
    profile_field,
    opportunity_field,
)


class Keyword(Base):
    """Normalized keyword/tag shared by profiles and opportunities."""
    __tablename__ = "keywords"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    value: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)

    profiles: Mapped[List["AcademicProfile"]] = relationship(
        secondary=profile_keyword, back_populates="keywords",
    )
    opportunities: Mapped[List["FundingOpportunity"]] = relationship(
        secondary=opportunity_keyword, back_populates="keywords",
    )


class ResearchField(Base):
    """Normalized research field / discipline shared by profiles and opportunities."""
    __tablename__ = "research_fields"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(300), nullable=False, unique=True)
    parent_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("research_fields.id", ondelete="SET NULL"), default=None,
    )

    profiles: Mapped[List["AcademicProfile"]] = relationship(
        secondary=profile_field, back_populates="fields",
    )
    opportunities: Mapped[List["FundingOpportunity"]] = relationship(
        secondary=opportunity_field, back_populates="fields",
    )


# Import all models so Base.metadata knows about every table
from backend.models.academic_profile import AcademicProfile  # noqa: E402, F401
from backend.models.funding_opportunity import FundingOpportunity  # noqa: E402, F401
from backend.models.data_source import DataSource  # noqa: E402, F401
from backend.models.match import Match  # noqa: E402, F401
