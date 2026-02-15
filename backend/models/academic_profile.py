from __future__ import annotations

import enum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import String, Text, Enum as SAEnum, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import Base
from backend.db.mixins import TimestampMixin
from backend.models.associations import profile_keyword, profile_field

if TYPE_CHECKING:
    from backend.models.match import Match


class CareerStage(str, enum.Enum):
    PHD_STUDENT = "phd_student"
    POSTDOC = "postdoc"
    EARLY_CAREER = "early_career"
    MID_CAREER = "mid_career"
    SENIOR = "senior"
    EMERITUS = "emeritus"


class AcademicProfile(TimestampMixin, Base):
    __tablename__ = "academic_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Identity
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    email: Mapped[str] = mapped_column(String(320), nullable=False, unique=True)

    # Academic details
    career_stage: Mapped[Optional[CareerStage]] = mapped_column(
        SAEnum(CareerStage, values_callable=lambda e: [x.value for x in e]),
        default=None,
    )
    institution: Mapped[Optional[str]] = mapped_column(String(300), default=None)
    department: Mapped[Optional[str]] = mapped_column(String(300), default=None)
    bio: Mapped[Optional[str]] = mapped_column(Text, default=None)
    publications_summary: Mapped[Optional[str]] = mapped_column(Text, default=None)
    orcid: Mapped[Optional[str]] = mapped_column(String(19), default=None, unique=True)

    # Notification preferences
    notify_email: Mapped[bool] = mapped_column(default=True, server_default="1")
    match_threshold: Mapped[float] = mapped_column(
        Float, default=0.5, server_default="0.5",
    )

    # Relationships
    keywords: Mapped[List["Keyword"]] = relationship(
        secondary=profile_keyword, back_populates="profiles", lazy="selectin",
    )
    fields: Mapped[List["ResearchField"]] = relationship(
        secondary=profile_field, back_populates="profiles", lazy="selectin",
    )
    matches: Mapped[List["Match"]] = relationship(back_populates="profile")

    def __repr__(self) -> str:
        return f"<AcademicProfile id={self.id} name={self.name!r}>"


# Avoid circular import — Keyword and ResearchField are defined in models/__init__.py
from backend.models import Keyword, ResearchField  # noqa: E402, F401
