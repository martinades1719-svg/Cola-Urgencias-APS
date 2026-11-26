from datetime import datetime
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
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Alert(Base):
    __tablename__ = "alerts"

    __table_args__ = (
        CheckConstraint(
            """
            alert_type IN (
                'LONG_WAIT',
                'REASSESSMENT',
                'CALLED_DELAY'
            )
            """,
            name="ck_alerts_valid_type",
        ),
        CheckConstraint(
            """
            status IN (
                'OPEN',
                'TAKEN',
                'RESOLVED'
            )
            """,
            name="ck_alerts_valid_status",
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

    alert_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
    )

    severity: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="MEDIUM",
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="OPEN",
        index=True,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    taken_by: Mapped[UUID | None] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    resolved_by: Mapped[UUID | None] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )

    taken_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )