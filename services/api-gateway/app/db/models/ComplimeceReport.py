from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import JSON, TIMESTAMP, Float, VARCHAR, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
import sqlalchemy as sa
from app.db.base import Base

class ComplianceReport(Base):
    __tablename__ = "compliance_reports"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    tenant_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("tenants.id"),
        nullable=False
    )

    document_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("documents.id"),
        nullable=False
    )

    summary: Mapped[dict] = mapped_column(JSON, nullable=False, server_default=sa.text("'{}'::jsonb"))
    findings: Mapped[dict] = mapped_column(JSON, nullable=False, server_default=sa.text("'{}'::jsonb"))

    compliance_score: Mapped[float] = mapped_column(Float, nullable=False)

    status: Mapped[str] = mapped_column(VARCHAR(50), nullable=False)
    generated_by: Mapped[str] = mapped_column(VARCHAR(100), nullable=False)

    metadata_: Mapped[dict] = mapped_column(JSON, nullable=False, server_default=sa.text("'{}'::jsonb"))

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False, server_default=sa.text('now()'))
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False, server_default=sa.text('now()'))

    # Relations
    tenant = relationship("Tenant", back_populates="compliance_reports")
    document = relationship("Document", back_populates="compliance_reports")
