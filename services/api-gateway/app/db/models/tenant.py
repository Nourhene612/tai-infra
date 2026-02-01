from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String
from app.db.base import Base

class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
