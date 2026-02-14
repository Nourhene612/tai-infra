from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy.orm import Mapped, mapped_column, relationship
import sqlalchemy as sa
from sqlalchemy import String, JSON, VARCHAR, TIMESTAMP, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.db.base import Base

class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    email: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    subscription_plan: Mapped[str] = mapped_column(VARCHAR(50), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=sa.text('true'))
    metadata_: Mapped[dict] = mapped_column(JSON, nullable=False, server_default=sa.text("'{}'::jsonb"))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False, server_default=sa.text('now()'))
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False, server_default=sa.text('now()'))

    # Relations
    users = relationship("User", back_populates="tenant")
    documents = relationship("Document", back_populates="tenant")
    roles = relationship("Role", back_populates="tenant")
    auth_sessions = relationship("AuthSession", back_populates="tenant")
    audit_logs = relationship("AuditLog", back_populates="tenant")
    company_assets = relationship("CompanyAsset", back_populates="tenant")
    proposals = relationship("Proposal", back_populates="tenant")
    compliance_reports = relationship("ComplianceReport", back_populates="tenant")
