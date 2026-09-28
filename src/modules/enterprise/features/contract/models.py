"""Contract model for the enterprise module."""

from decimal import Decimal
from typing import Optional

from sqlalchemy import Boolean, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING, List

from src.shared.database.sql_client import Base
from src.shared.database.sql_mixins import SoftDeleteMixin

if TYPE_CHECKING:
    from src.modules.enterprise.features.vacancy.models import Vacancy


class Contract(Base, SoftDeleteMixin):
    """Employment contract terms."""

    __tablename__ = "Contract"
    __table_args__ = {"schema": "enterprise"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    type: Mapped[str] = mapped_column(String(25), nullable=False)
    regional_classification: Mapped[str] = mapped_column(String(4), nullable=False)
    currency: Mapped[str] = mapped_column(String(4), nullable=False, default="BRL")
    payment_periodicity: Mapped[str] = mapped_column(String(25), nullable=False, default="MONTHLY")
    min_payment_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric, nullable=True)
    max_payment_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric, nullable=True)
    is_payment_disclosed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    vacancies: Mapped[List["Vacancy"]] = relationship("Vacancy", back_populates="contract")

    def __repr__(self) -> str:
        return f"<Contract(id={self.id}, type='{self.type}')>"
