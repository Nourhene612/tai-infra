from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, VARCHAR, ForeignKey, JSON, TIMESTAMP, Boolean
from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
import sqlalchemy as sa
from app.db.base import Base

class Document(Base):
    __tablename__ = "documents"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    created_by: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    updated_by: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    uploaded_by: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    file_name: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    storage_path: Mapped[str] = mapped_column(VARCHAR(500), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str] = mapped_column(VARCHAR(100), nullable=False)
    language: Mapped[str] = mapped_column(VARCHAR(10), nullable=False)
    status: Mapped[str] = mapped_column(VARCHAR(50), nullable=False)

    metadata_: Mapped[dict] = mapped_column(JSON, nullable=False, server_default=sa.text("'{}'::jsonb"))
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=sa.text('false'))

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False, server_default=sa.text('now()'))
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False, server_default=sa.text('now()'))

    tenant = relationship("Tenant", back_populates="documents")
    creator = relationship("User", foreign_keys=[created_by], back_populates="documents_created")
    updater = relationship("User", foreign_keys=[updated_by], back_populates="documents_updated")
    uploader = relationship("User", foreign_keys=[uploaded_by], back_populates="documents_uploaded")
    proposals = relationship("Proposal", back_populates="document")
    compliance_reports = relationship("ComplianceReport", back_populates="document")
