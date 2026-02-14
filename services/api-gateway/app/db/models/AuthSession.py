from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import INET, UUID as PG_UUID
from app.db.base import Base
import sqlalchemy as sa

class AuthSession(Base):
    __tablename__ = "auth_sessions"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=sa.text('gen_random_uuid()')
    )

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    tenant_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False
    )

    jti: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
        unique=True,
        default=uuid4,
        comment="JWT ID for refresh token"
    )

    user_agent: Mapped[str] = mapped_column(Text, nullable=True, comment="Browser/device user agent")
    ip_address: Mapped[str] = mapped_column(INET, nullable=True, comment="IP address of session creation")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=sa.text('NOW()')
    )

    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, comment="Refresh token expiration")
    revoked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True, comment="When session was revoked")
    replaced_by: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=True, comment="ID of session that replaced this one (rotation)")
    last_used_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True, comment="Last time this session was used")

    # Relations
    user = relationship("User", back_populates="auth_sessions")
    tenant = relationship("Tenant", back_populates="auth_sessions")
