"""Location model for the enterprise module."""

from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.shared.database.sql_client import Base
from src.shared.database.sql_mixins import SoftDeleteMixin

if TYPE_CHECKING:
    from src.modules.enterprise.features.company.models import CompanyUnit


class Location(Base, SoftDeleteMixin):
    """Physical address / location."""

    __tablename__ = "Location"
    __table_args__ = {"schema": "enterprise"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    country: Mapped[str] = mapped_column(String(4), nullable=False)
    state: Mapped[str] = mapped_column(String(25), nullable=False)
    city: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    neighborhood: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    postal_code: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    street: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    number: Mapped[Optional[str]] = mapped_column(String(15), nullable=True)
    complement: Mapped[Optional[str]] = mapped_column(String(25), nullable=True)

    company_units: Mapped[List["CompanyUnit"]] = relationship(
        "CompanyUnit", back_populates="location"
    )

    def __repr__(self) -> str:
        return f"<Location(id={self.id}, city='{self.city}', country='{self.country}')>"
