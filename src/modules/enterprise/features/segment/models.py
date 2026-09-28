"""Segment model for the enterprise module."""

from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.shared.database.sql_client import Base
from src.shared.database.sql_mixins import SoftDeleteMixin

if TYPE_CHECKING:
    from src.modules.enterprise.features.company.models import CompanySegment


class Segment(Base, SoftDeleteMixin):
    """Industry / market segment."""

    __tablename__ = "Segment"
    __table_args__ = {"schema": "enterprise"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    company_segments: Mapped[List["CompanySegment"]] = relationship(
        "CompanySegment", back_populates="segment"
    )

    def __repr__(self) -> str:
        return f"<Segment(id={self.id}, name='{self.name}')>"
