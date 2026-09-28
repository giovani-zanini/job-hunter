from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List

from src.shared.database.sql_client import Base
from src.shared.database.sql_mixins import SoftDeleteMixin


class User(Base, SoftDeleteMixin):
    """User model representing profile module users.

    Each row is created automatically on the first authenticated request and
    maps 1-to-1 to an ``auth.User`` record via ``external_id``.
    """

    __tablename__ = "User"
    __table_args__ = {"schema": "profile"}

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Columns
    external_id: Mapped[int] = mapped_column(
        Integer, unique=True, nullable=False, index=True
    )

    # Relationships
    profiles: Mapped[List["Profile"]] = relationship(
        "Profile", back_populates="user", cascade="all, delete-orphan"
    )

    links: Mapped[List["Link"]] = relationship(
        "Link", back_populates="user", cascade="all, delete-orphan"
    )

    experiences: Mapped[List["Experience"]] = relationship(
        "Experience", back_populates="user", cascade="all, delete-orphan"
    )

    educations: Mapped[List["Education"]] = relationship(
        "Education", back_populates="user", cascade="all, delete-orphan"
    )

    certificates: Mapped[List["Certificate"]] = relationship(
        "Certificate", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, external_id={self.external_id})>"
