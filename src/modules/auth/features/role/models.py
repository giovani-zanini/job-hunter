"""Role model for the auth module."""

from sqlalchemy import String, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.database.sql_client import Base
from src.shared.database.sql_mixins import SoftDeleteMixin, TimestampMixin


class Role(Base, SoftDeleteMixin, TimestampMixin):
    """Role model representing user roles for RBAC."""

    __tablename__ = "Role"
    __table_args__ = {"schema": "auth"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<Role(id={self.id}, name='{self.name}')>"
