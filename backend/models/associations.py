"""Many-to-many association tables for shared taxonomy (keywords, research fields)."""

from sqlalchemy import Table, Column, Integer, ForeignKey
from backend.db.base import Base

profile_keyword = Table(
    "profile_keyword",
    Base.metadata,
    Column("profile_id", Integer, ForeignKey("academic_profiles.id", ondelete="CASCADE"), primary_key=True),
    Column("keyword_id", Integer, ForeignKey("keywords.id", ondelete="CASCADE"), primary_key=True),
)

opportunity_keyword = Table(
    "opportunity_keyword",
    Base.metadata,
    Column("opportunity_id", Integer, ForeignKey("funding_opportunities.id", ondelete="CASCADE"), primary_key=True),
    Column("keyword_id", Integer, ForeignKey("keywords.id", ondelete="CASCADE"), primary_key=True),
)

profile_field = Table(
    "profile_field",
    Base.metadata,
    Column("profile_id", Integer, ForeignKey("academic_profiles.id", ondelete="CASCADE"), primary_key=True),
    Column("field_id", Integer, ForeignKey("research_fields.id", ondelete="CASCADE"), primary_key=True),
)

opportunity_field = Table(
    "opportunity_field",
    Base.metadata,
    Column("opportunity_id", Integer, ForeignKey("funding_opportunities.id", ondelete="CASCADE"), primary_key=True),
    Column("field_id", Integer, ForeignKey("research_fields.id", ondelete="CASCADE"), primary_key=True),
)
