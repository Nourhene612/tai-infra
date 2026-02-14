from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, JSON, VARCHAR, TIMESTAMP, Boolean, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
import sqlalchemy as sa

from app.db.base import Base

class Proposal(Base):
    __tablename__ = "proposals"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    document_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    created_by: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    title: Mapped[str] = mapped_column(VARCHAR(500), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    storage_path: Mapped[str] = mapped_column(VARCHAR(500), nullable=False)
    status: Mapped[str] = mapped_column(VARCHAR(50), nullable=False)
    metadata_: Mapped[dict] = mapped_column(JSON, nullable=False, server_default=sa.text("'{}'::jsonb"))
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=sa.text('false'))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False, server_default=sa.text('now()'))
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False, server_default=sa.text('now()'))

    # Relations
    tenant = relationship("Tenant", back_populates="proposals")
    document = relationship("Document", back_populates="proposals")
    creator = relationship("User", back_populates="proposals_created")
