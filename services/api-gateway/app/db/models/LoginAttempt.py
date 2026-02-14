from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import INET, UUID as PG_UUID
import sqlalchemy as sa

from app.db.base import Base


class LoginAttempt(Base):
    __tablename__ = "login_attempts"

    # ID principal UUID
    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    # ID utilisateur (nullable si l'email n'existe pas)
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
        comment="NULL if user not found"
    )

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Email attempted"
    )

    ip_address: Mapped[str] = mapped_column(
        INET,
        nullable=True,
        comment="IP address of attempt"
    )

    user_agent: Mapped[str] = mapped_column(
        Text,
        nullable=True,
        comment="Browser/device user agent"
    )

    success: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=sa.text('false'),
        comment="Whether login succeeded"
    )

    failure_reason: Mapped[str] = mapped_column(
        String(100),
        nullable=True,
        comment="Reason for failure (invalid_credentials, rate_limited, etc.)"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=sa.text('NOW()')
    )

    # Relation avec l'utilisateur
    user = relationship("User", foreign_keys=[user_id])
