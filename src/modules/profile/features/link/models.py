"""Link models for the job-finder application.

Defines the SQLAlchemy models for user links and profile-link associations,
including soft-deletion behavior and relationship mappings.
"""

from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING, List

from src.shared.database.sql_client import Base
from src.shared.database.sql_mixins import SoftDeleteMixin

if TYPE_CHECKING:
    from src.modules.profile.features.user.models import User
    from src.modules.profile.features.profile.models import Profile


class Link(Base, SoftDeleteMixin):
    """Represents a user's external link (social media, email, phone, etc.).

    Includes soft-deletion behavior via ``SoftDeleteMixin``.

    Attributes:
        id: Primary key identifier.
        user_id: Foreign key to ``User.id``.
        type: Type of link (SOCIAL_MEDIA, EMAIL, CELLPHONE).
        from_: Origin platform (gmail, linkedin, instagram, etc.).
        value: The actual link/value (URL, email, phone number).

    Relationships:
        user: Owner user for this link.
        profile_links: Profile associations for this link.
    """

    __tablename__ = "Link"
    __table_args__ = {"schema": "profile"}

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Foreign Keys
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("profile.User.id"), nullable=False
    )

    # Columns
    type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Indica o tipo de link: Exemplo: SOCIAL_MEDIA, EMAIL, CELLPHONE",
    )
    from_: Mapped[str] = mapped_column(
        "from",
        String(50),
        nullable=False,
        comment="Indica o local de origem. Exemplo: gmail, outlook, Linkedin, Instagram, etc...",
    )
    value: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        comment="Indica o link na sua forma bruta. Exemplo: www.portfolio.com, 47988000554",
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="links")

    profile_links: Mapped[List["ProfileLink"]] = relationship(
        "ProfileLink",
        back_populates="link",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """Return a concise string representation.

        Returns:
            A string with the link id, type, and origin.
        """
        return f"<Link(id={self.id}, type='{self.type}', from='{self.from_}')>"


class ProfileLink(Base):
    """Links profiles to external links.

    Represents the many-to-many relationship between profiles and links,
    allowing a single link to be associated with multiple profiles.

    Attributes:
        id: Primary key identifier.
        link_id: Foreign key to ``Link.id``.
        profile_id: Foreign key to ``Profile.id``.

    Relationships:
        link: Associated link.
        profile: Associated profile.
    """

    __tablename__ = "ProfileLink"
    __table_args__ = {"schema": "profile"}

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Foreign Keys
    link_id: Mapped[int] = mapped_column(ForeignKey("profile.Link.id"), nullable=False)
    profile_id: Mapped[int] = mapped_column(
        ForeignKey("profile.Profile.id"), nullable=False
    )

    # Relationships
    link: Mapped["Link"] = relationship("Link", back_populates="profile_links")
    profile: Mapped["Profile"] = relationship("Profile", back_populates="profile_links")

    def __repr__(self) -> str:
        """Return a concise string representation.

        Returns:
            A string with the profile id and link id.
        """
        return f"<ProfileLink(profile_id={self.profile_id}, link_id={self.link_id})>"
