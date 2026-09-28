"""Requirement model for the enterprise module."""

from typing import TYPE_CHECKING, List

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.shared.database.sql_client import Base
from src.shared.database.sql_mixins import SoftDeleteMixin

if TYPE_CHECKING:
    from src.modules.enterprise.features.vacancy.models import VacancyRequirement


class Requirement(Base, SoftDeleteMixin):
    """A skill/knowledge requirement for a job vacancy."""

    __tablename__ = "Requirement"
    __table_args__ = {"schema": "enterprise"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    skill: Mapped[str] = mapped_column(String(50), nullable=False)

    vacancy_requirements: Mapped[List["VacancyRequirement"]] = relationship(
        "VacancyRequirement", back_populates="requirement",
        foreign_keys="VacancyRequirement.requirement_id",
    )

    def __repr__(self) -> str:
        return f"<Requirement(id={self.id}, skill='{self.skill}')>"
