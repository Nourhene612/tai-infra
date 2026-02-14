
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, JSON, VARCHAR, TIMESTAMP, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
import sqlalchemy as sa

from app.db.base import Base

class Role(Base):
    __tablename__ = "roles"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)

    name: Mapped[str] = mapped_column(VARCHAR(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    permissions: Mapped[dict] = mapped_column(JSON, nullable=False, server_default=sa.text("'{}'::jsonb"))
    is_system: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=sa.text('false'))

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False, server_default=sa.text('now()'))
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False, server_default=sa.text('now()'))

    # Relations
    tenant = relationship("Tenant", back_populates="roles")
    users = relationship("User", back_populates="role")
