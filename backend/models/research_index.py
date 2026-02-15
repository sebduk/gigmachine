"""
Research index — extracted research fingerprint from uploaded documents.

When a user uploads a CV, publication list, or links to their work,
we process the document and extract ONLY research-relevant content:
  - topics, methodologies, techniques mentioned
  - research domains and sub-fields
  - type of work (theoretical, experimental, applied, etc.)

The original document is NOT stored. Personal details (names, addresses,
phone numbers, institutional affiliations) are stripped during ingestion.
Only the anonymized research fingerprint remains.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, String, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import Base
from backend.db.mixins import TimestampMixin

if TYPE_CHECKING:
    from backend.models.academic_profile import AcademicProfile


class ResearchIndex(TimestampMixin, Base):
    __tablename__ = "research_index"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    profile_id: Mapped[int] = mapped_column(
        ForeignKey("academic_profiles.id", ondelete="CASCADE"), nullable=False,
    )

    # What kind of source was this extracted from?
    source_type: Mapped[str] = mapped_column(
        String(50), nullable=False,
        comment="cv, publication, grant_history, manual",
    )

    # The extracted, anonymized research content
    extracted_topics: Mapped[Optional[str]] = mapped_column(
        Text, default=None,
        comment="JSON array of research topics extracted from the document",
    )
    extracted_methods: Mapped[Optional[str]] = mapped_column(
        Text, default=None,
        comment="JSON array of methodologies/techniques mentioned",
    )
    extracted_domains: Mapped[Optional[str]] = mapped_column(
        Text, default=None,
        comment="JSON array of research domains identified",
    )
    work_type: Mapped[Optional[str]] = mapped_column(
        String(100), default=None,
        comment="theoretical, experimental, applied, computational, etc.",
    )
    experience_years: Mapped[Optional[int]] = mapped_column(
        Integer, default=None,
        comment="Approximate years of research experience (range, not exact)",
    )
    summary: Mapped[Optional[str]] = mapped_column(
        Text, default=None,
        comment="AI-generated summary of research focus. No PII.",
    )

    # Audit: hash of original document (for dedup), but NOT the document itself
    source_hash: Mapped[Optional[str]] = mapped_column(
        String(64), default=None,
        comment="SHA-256 of original document for deduplication. Document itself is discarded.",
    )

    # Relationship
    profile: Mapped["AcademicProfile"] = relationship(back_populates="research_entries")

    def __repr__(self) -> str:
        return f"<ResearchIndex id={self.id} profile={self.profile_id} type={self.source_type}>"
