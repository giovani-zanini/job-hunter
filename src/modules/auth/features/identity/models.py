"""Auth model for credential management."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.shared.database.sql_client import Base
from src.shared.database.sql_mixins import TimestampMixin, SoftDeleteMixin


class Auth(Base, SoftDeleteMixin, TimestampMixin):
    """Auth model storing user credentials and recovery information."""

    __tablename__ = "Auth"
    __table_args__ = {"schema": "auth"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("auth.User.id", ondelete="CASCADE"), nullable=False
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    failed_login_attempts: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    locked_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    recovery_token: Mapped[str | None] = mapped_column(String(100), nullable=True)
    recovery_token_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    user = relationship("UserAccount", back_populates="auth", lazy="joined")

    def __repr__(self) -> str:
        return f"<Auth(id={self.id}, user_id={self.user_id})>"
