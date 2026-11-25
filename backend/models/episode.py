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
    from models.patient import Patient
    from models.user import User


class Episode(Base):
    __tablename__ = "episodes"

    __table_args__ = (
        CheckConstraint(
            """
            status IN (
                'PENDING_TRIAGE',
                'WAITING',
                'CALLED',
                'IN_CARE',
                'CLOSED',
                'WITHDRAWN'
            )
            """,
            name="ck_episodes_valid_status",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    patient_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "patients.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    created_by: Mapped[UUID | None] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    ticket: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
    )

    public_token_hash: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="PENDING_TRIAGE",
        index=True,
    )

    arrived_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    triage_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    called_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    care_started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    closed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    box: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    closure_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    patient: Mapped["Patient"] = relationship(
        back_populates="episodes",
    )

    creator: Mapped["User | None"] = relationship()