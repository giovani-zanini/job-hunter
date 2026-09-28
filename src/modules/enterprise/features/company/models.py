"""Company models for the enterprise module."""

from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.shared.database.sql_client import Base
from src.shared.database.sql_mixins import SoftDeleteMixin

if TYPE_CHECKING:
    from src.modules.enterprise.features.location.models import Location
    from src.modules.enterprise.features.segment.models import Segment
    from src.modules.enterprise.features.vacancy.models import Vacancy
    from src.modules.enterprise.features.meta.models import Meta


class EnterpriseCompany(Base, SoftDeleteMixin):
    """Enterprise company."""

    __tablename__ = "Company"
    __table_args__ = {"schema": "enterprise"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)

    units: Mapped[List["CompanyUnit"]] = relationship(
        "CompanyUnit", back_populates="company", cascade="all, delete-orphan"
    )
    company_segments: Mapped[List["CompanySegment"]] = relationship(
        "CompanySegment", back_populates="company", cascade="all, delete-orphan"
    )
    metas: Mapped[List["Meta"]] = relationship("Meta", back_populates="company")

    def __repr__(self) -> str:
        return f"<EnterpriseCompany(id={self.id}, name='{self.name}')>"


class CompanyUnit(Base):
    """Company + Location pair (physical branch)."""

    __tablename__ = "CompanyUnit"
    __table_args__ = (
        UniqueConstraint("company_id", "location_id", name="uq_company_unit"),
        {"schema": "enterprise"},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(
        ForeignKey("enterprise.Company.id"), nullable=False
    )
    location_id: Mapped[int] = mapped_column(
        ForeignKey("enterprise.Location.id"), nullable=False
    )

    company: Mapped["EnterpriseCompany"] = relationship("EnterpriseCompany", back_populates="units")
    location: Mapped["Location"] = relationship("Location", back_populates="company_units")
    vacancies: Mapped[List["Vacancy"]] = relationship("Vacancy", back_populates="company_unit")

    def __repr__(self) -> str:
        return f"<CompanyUnit(id={self.id}, company_id={self.company_id}, location_id={self.location_id})>"


class CompanySegment(Base):
    """Company ↔ Segment M2M association."""

    __tablename__ = "CompanySegment"
    __table_args__ = (
        UniqueConstraint("company_id", "segment_id", name="uq_company_segment"),
        {"schema": "enterprise"},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(
        ForeignKey("enterprise.Company.id"), nullable=False
    )
    segment_id: Mapped[int] = mapped_column(
        ForeignKey("enterprise.Segment.id"), nullable=False
    )

    company: Mapped["EnterpriseCompany"] = relationship("EnterpriseCompany", back_populates="company_segments")
    segment: Mapped["Segment"] = relationship("Segment", back_populates="company_segments")

    def __repr__(self) -> str:
        return f"<CompanySegment(company_id={self.company_id}, segment_id={self.segment_id})>"
