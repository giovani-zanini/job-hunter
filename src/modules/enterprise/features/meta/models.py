"""Meta model for the enterprise module."""

from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.shared.database.sql_client import Base
from src.shared.database.sql_mixins import SoftDeleteMixin

if TYPE_CHECKING:
    from src.modules.enterprise.features.vacancy.models import Vacancy
    from src.modules.enterprise.features.company.models import EnterpriseCompany


class Meta(Base, SoftDeleteMixin):
    """Metadata about a job vacancy or company (extraction/parsing info)."""

    __tablename__ = "Meta"
    __table_args__ = (
        UniqueConstraint("vacancy_id", name="uq_meta_vacancy"),
        UniqueConstraint("company_id", name="uq_meta_company"),
        {"schema": "enterprise"},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    app_version: Mapped[str] = mapped_column(String(25), nullable=False, default="1.0.0")
    extraction_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    parsing_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    source_url: Mapped[str] = mapped_column(Text, nullable=False)
    custom_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    vacancy_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("enterprise.Vacancy.id"), nullable=True
    )
    company_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("enterprise.Company.id"), nullable=True
    )

    vacancy: Mapped[Optional["Vacancy"]] = relationship("Vacancy", back_populates="meta")
    company: Mapped[Optional["EnterpriseCompany"]] = relationship("EnterpriseCompany", back_populates="metas")

    def __repr__(self) -> str:
        return f"<Meta(id={self.id}, vacancy_id={self.vacancy_id}, company_id={self.company_id})>"
