from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, JSON, VARCHAR, TIMESTAMP, Boolean, TEXT
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
import sqlalchemy as sa
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    role_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("roles.id"), nullable=False)
    email: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    full_name: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=sa.text('true'))
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=sa.text('false'))
    last_login_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=True)
    metadata_: Mapped[dict] = mapped_column(JSON, nullable=False, server_default=sa.text("'{}'::jsonb"))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False, server_default=sa.text('now()'))
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False, server_default=sa.text('now()'))
    totp_secret: Mapped[str] = mapped_column(VARCHAR(64), nullable=True)
    totp_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=sa.text('true'))
    totp_verified_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=True)
    totp_setup_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=True)
    backup_codes: Mapped[list[str]] = mapped_column(ARRAY(TEXT), nullable=True)

    # Relations
    tenant = relationship("Tenant", back_populates="users")
    role = relationship("Role", back_populates="users")
    documents_uploaded = relationship("Document", foreign_keys="Document.uploaded_by", back_populates="uploader")
    documents_created = relationship("Document", foreign_keys="Document.created_by", back_populates="creator")
    documents_updated = relationship("Document", foreign_keys="Document.updated_by", back_populates="updater")
    auth_sessions = relationship("AuthSession", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")
    created_assets = relationship("CompanyAsset", foreign_keys="CompanyAsset.created_by", back_populates="creator")
    updated_assets = relationship("CompanyAsset", foreign_keys="CompanyAsset.updated_by", back_populates="updater")
    proposals_created = relationship("Proposal", back_populates="creator")
