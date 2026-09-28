"""Company model for the job-finder application."""

from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING, List

from src.shared.database.sql_client import Base
from src.shared.database.sql_mixins import SoftDeleteMixin

if TYPE_CHECKING:
    from src.modules.profile.features.experience.models import Experience


class Company(Base, SoftDeleteMixin):
    """Company model representing organizations where users have worked."""

    __tablename__ = "Company"
    __table_args__ = {"schema": "profile"}

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Columns
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    website: Mapped[str] = mapped_column(String(255), nullable=False)

    # Relationships
    experiences: Mapped[List["Experience"]] = relationship(
        "Experience", back_populates="company", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Company(id={self.id}, name='{self.name}')>"
