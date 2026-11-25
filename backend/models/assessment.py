from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


if TYPE_CHECKING:
    from models.episode import Episode
    from models.user import User


class Assessment(Base):
    __tablename__ = "assessments"

    __table_args__ = (
        CheckConstraint(
            "priority IN ('C1', 'C2', 'C3', 'C4', 'C5')",
            name="ck_assessments_valid_priority",
        ),
        CheckConstraint(
            "assessment_type IN ('INITIAL', 'REASSESSMENT')",
            name="ck_assessments_valid_type",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    episode_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "episodes.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    assessed_by: Mapped[UUID] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    assessment_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    priority: Mapped[str] = mapped_column(
        String(2),
        nullable=False,
        index=True,
    )

    previous_priority: Mapped[str | None] = mapped_column(
        String(2),
        nullable=True,
    )

    observation: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    change_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    assessed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )

    episode: Mapped["Episode"] = relationship(
        back_populates="assessments",
    )

    assessor: Mapped["User"] = relationship()
