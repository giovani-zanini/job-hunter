"""Responsability model for the enterprise module."""

from typing import TYPE_CHECKING, List

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.shared.database.sql_client import Base
from src.shared.database.sql_mixins import SoftDeleteMixin

if TYPE_CHECKING:
    from src.modules.enterprise.features.vacancy.models import VacancyResponsability


class Responsability(Base, SoftDeleteMixin):
    """An action/outcome responsibility associated with a job vacancy."""

    __tablename__ = "Responsability"
    __table_args__ = {"schema": "enterprise"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    target: Mapped[str] = mapped_column(String(50), nullable=False)
    outcome: Mapped[str] = mapped_column(String(50), nullable=False)

    vacancy_responsabilities: Mapped[List["VacancyResponsability"]] = relationship(
        "VacancyResponsability", back_populates="responsability"
    )

    def __repr__(self) -> str:
        return f"<Responsability(id={self.id}, action='{self.action}')>"
