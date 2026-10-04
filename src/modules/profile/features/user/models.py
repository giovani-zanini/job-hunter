from sqlalchemy import Boolean, Integer, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List

from src.shared.database.sql_client import Base
from src.shared.database.sql_mixins import SoftDeleteMixin


class User(Base, SoftDeleteMixin):
    """Local owner row for profile records, including the anonymous owner."""

    __tablename__ = "User"
    __table_args__ = {"schema": "profile"}

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Columns
    is_anonymous: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
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
        return f"<User(id={self.id}, is_anonymous={self.is_anonymous})>"


Index(
    "uq_profile_User_anonymous",
    User.is_anonymous,
    unique=True,
    postgresql_where=User.is_anonymous.is_(True),
)
