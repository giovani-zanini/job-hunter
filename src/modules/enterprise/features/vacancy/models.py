"""Vacancy models for the enterprise module."""

from datetime import date
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import (
    Date,
    ForeignKey,
    Integer,
    JSON,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.shared.database.sql_client import Base
from src.shared.database.sql_mixins import SoftDeleteMixin

if TYPE_CHECKING:
    from src.modules.enterprise.features.company.models import CompanyUnit
    from src.modules.enterprise.features.contract.models import Contract
    from src.modules.enterprise.features.requirement.models import Requirement
    from src.modules.enterprise.features.responsability.models import Responsability
    from src.modules.enterprise.features.meta.models import Meta


class Vacancy(Base, SoftDeleteMixin):
    """A job vacancy posted by a company unit."""

    __tablename__ = "Vacancy"
    __table_args__ = {"schema": "enterprise"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    company_unit_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("enterprise.CompanyUnit.id"), nullable=False
    )
    contract_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("enterprise.Contract.id"), nullable=True
    )
    seniority_level: Mapped[str] = mapped_column(String(25), nullable=False)
    published_date: Mapped[date] = mapped_column(Date, nullable=False)
    custom_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    company_unit: Mapped["CompanyUnit"] = relationship("CompanyUnit", back_populates="vacancies")
    contract: Mapped[Optional["Contract"]] = relationship("Contract", back_populates="vacancies")
    vacancy_requirements: Mapped[List["VacancyRequirement"]] = relationship(
        "VacancyRequirement", back_populates="vacancy", cascade="all, delete-orphan"
    )
    vacancy_responsabilities: Mapped[List["VacancyResponsability"]] = relationship(
        "VacancyResponsability", back_populates="vacancy", cascade="all, delete-orphan"
    )
    meta: Mapped[Optional["Meta"]] = relationship("Meta", back_populates="vacancy", uselist=False)

    def __repr__(self) -> str:
        return f"<Vacancy(id={self.id}, title='{self.title}')>"


class VacancyRequirement(Base):
    """Association between a vacancy and a requirement."""

    __tablename__ = "VacancyRequirement"
    __table_args__ = {"schema": "enterprise"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    vacancy_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("enterprise.Vacancy.id"), nullable=False
    )
    requirement_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("enterprise.Requirement.id"), nullable=False
    )
    optional_requirement_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("enterprise.Requirement.id"), nullable=True
    )
    level: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    experience_years: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True)
    requirement_type: Mapped[str] = mapped_column(String(25), nullable=False)

    vacancy: Mapped["Vacancy"] = relationship("Vacancy", back_populates="vacancy_requirements")
    requirement: Mapped["Requirement"] = relationship(
        "Requirement", back_populates="vacancy_requirements", foreign_keys=[requirement_id]
    )
    optional_requirement: Mapped[Optional["Requirement"]] = relationship(
        "Requirement", foreign_keys=[optional_requirement_id]
    )

    def __repr__(self) -> str:
        return f"<VacancyRequirement(id={self.id}, vacancy_id={self.vacancy_id}, requirement_id={self.requirement_id})>"


class VacancyResponsability(Base):
    """Association between a vacancy and a responsability."""

    __tablename__ = "VacancyResponsability"
    __table_args__ = (
        UniqueConstraint("vacancy_id", "responsability_id", name="uq_vacancy_responsability"),
        {"schema": "enterprise"},
    )

    vacancy_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("enterprise.Vacancy.id"), primary_key=True
    )
    responsability_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("enterprise.Responsability.id"), primary_key=True
    )

    vacancy: Mapped["Vacancy"] = relationship("Vacancy", back_populates="vacancy_responsabilities")
    responsability: Mapped["Responsability"] = relationship(
        "Responsability", back_populates="vacancy_responsabilities"
    )

    def __repr__(self) -> str:
        return f"<VacancyResponsability(vacancy_id={self.vacancy_id}, responsability_id={self.responsability_id})>"
