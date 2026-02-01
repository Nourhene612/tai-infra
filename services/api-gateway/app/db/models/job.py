from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, ForeignKey
from app.db.base import Base

class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[str] = mapped_column(String, nullable=False)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), nullable=False)
