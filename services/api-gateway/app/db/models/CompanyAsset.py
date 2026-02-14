from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Integer, String, Text, Boolean, DateTime, CheckConstraint, JSON, ARRAY
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from app.db.base import Base

class CompanyAsset(Base):
    __tablename__ = "company_asset"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)

    kind: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=True, comment="Full text content for embedding")

    file_uri: Mapped[str] = mapped_column(Text, nullable=True, comment="MinIO path: tenants/{tenant_id}/assets/{filename}")
    file_type: Mapped[str] = mapped_column(String(50), nullable=True)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=True)

    metadata_: Mapped[dict] = mapped_column(JSON, nullable=False, server_default=sa.text("'{}'::jsonb"))
    tags: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=sa.text('true'))
    is_public: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=sa.text('false'))

    deleted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))

    created_by: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    updated_by: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    __table_args__ = (
        CheckConstraint(
            "kind IN ('certification', 'past_project', 'team_bio', 'company_description', "
            "'technical_capability', 'financial_document', 'legal_document', "
            "'standard_clause', 'logo', 'template', 'other')",
            name="ck_company_asset_kind"
        ),
    )

    tenant = relationship("Tenant", back_populates="company_assets")
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_assets")
    updater = relationship("User", foreign_keys=[updated_by], back_populates="updated_assets")
