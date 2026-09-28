"""User model for the auth module."""

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.shared.database.sql_client import Base
from src.shared.database.sql_mixins import TimestampMixin, SoftDeleteMixin


class UserAccount(Base, SoftDeleteMixin, TimestampMixin):
    """User model for authentication and authorization."""

    __tablename__ = "User"
    __table_args__ = {"schema": "auth"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    role_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("auth.Role.id"), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    role = relationship("Role", lazy="joined")
    auth = relationship("Auth", back_populates="user", lazy="joined")
    sessions = relationship("Session", back_populates="user", lazy="select")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}')>"
