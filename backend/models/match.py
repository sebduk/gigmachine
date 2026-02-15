from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Text, Float, String, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import Base
from backend.db.mixins import TimestampMixin

if TYPE_CHECKING:
    from backend.models.academic_profile import AcademicProfile
    from backend.models.funding_opportunity import FundingOpportunity


class Match(TimestampMixin, Base):
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    profile_id: Mapped[int] = mapped_column(
        ForeignKey("academic_profiles.id", ondelete="CASCADE"), nullable=False,
    )
    opportunity_id: Mapped[int] = mapped_column(
        ForeignKey("funding_opportunities.id", ondelete="CASCADE"), nullable=False,
    )

    # Matching metadata
    score: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    match_method: Mapped[str] = mapped_column(
        String(50), default="keyword", server_default="keyword",
    )
    match_reasons: Mapped[Optional[str]] = mapped_column(Text, default=None)

    # User interaction
    is_seen: Mapped[bool] = mapped_column(default=False, server_default="0")
    is_saved: Mapped[bool] = mapped_column(default=False, server_default="0")
    is_dismissed: Mapped[bool] = mapped_column(default=False, server_default="0")
    is_notified: Mapped[bool] = mapped_column(default=False, server_default="0")
    notified_at: Mapped[Optional[datetime]] = mapped_column(default=None)

    # Relationships
    profile: Mapped["AcademicProfile"] = relationship(back_populates="matches")
    opportunity: Mapped["FundingOpportunity"] = relationship(back_populates="matches")

    __table_args__ = (
        UniqueConstraint("profile_id", "opportunity_id", name="uq_profile_opportunity"),
        Index("ix_match_profile_score", "profile_id", "score"),
        Index("ix_match_unseen", "profile_id", "is_seen", "is_dismissed"),
    )

    def __repr__(self) -> str:
        return f"<Match profile={self.profile_id} opp={self.opportunity_id} score={self.score:.2f}>"
