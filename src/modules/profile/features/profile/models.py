"""Profile models for the job-finder application.

Defines the SQLAlchemy models for user profiles and profile skills,
including soft-deletion behavior and relationship mappings.
"""

from sqlalchemy import String, Integer, Text, Date, SmallInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING, List, Optional
from datetime import date

from src.shared.database.sql_client import Base
from src.shared.database.sql_mixins import SoftDeleteMixin

if TYPE_CHECKING:
    from src.modules.profile.features.user.models import User
    from src.modules.profile.features.skill.models import Skill
    from src.modules.profile.features.link.models import ProfileLink
    from src.modules.profile.features.experience.models import ProfileExperience
    from src.modules.profile.features.education.models import ProfileEducation
    from src.modules.profile.features.certificate.models import ProfileCertificate


class Profile(Base, SoftDeleteMixin):
    """Represents a user's professional profile.

    Includes soft-deletion behavior via ``SoftDeleteMixin``.

    Attributes:
        id: Primary key identifier.
        user_id: Foreign key to ``User.id``.
        slug: URL-friendly profile identifier.
        full_name: User's full name.
        title: Professional headline or role.
        bio: Profile biography text.

    Relationships:
        user: Owner user for this profile.
        profile_skills: Skill associations for the profile.
        profile_experiences: Experience entries for the profile.
        profile_educations: Education entries for the profile.
        profile_certificates: Certificate entries for the profile.
        profile_links: External links for the profile.
    """

    __tablename__ = "Profile"
    __table_args__ = {"schema": "profile"}

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Foreign Keys
    user_id: Mapped[int] = mapped_column(ForeignKey("profile.User.id"), nullable=False)

    # Columns
    slug: Mapped[str] = mapped_column(String(25), nullable=False)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    title: Mapped[str] = mapped_column(String(125), nullable=False)
    bio: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="profiles")

    profile_skills: Mapped[List["ProfileSkills"]] = relationship(
        "ProfileSkills",
        back_populates="profile",
        cascade="all, delete-orphan",
    )

    profile_experiences: Mapped[List["ProfileExperience"]] = relationship(
        "ProfileExperience",
        back_populates="profile",
        cascade="all, delete-orphan",
    )

    profile_educations: Mapped[List["ProfileEducation"]] = relationship(
        "ProfileEducation",
        back_populates="profile",
        cascade="all, delete-orphan",
    )

    profile_certificates: Mapped[List["ProfileCertificate"]] = relationship(
        "ProfileCertificate",
        back_populates="profile",
        cascade="all, delete-orphan",
    )

    profile_links: Mapped[List["ProfileLink"]] = relationship(
        "ProfileLink",
        back_populates="profile",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """Return a concise string representation.

        Returns:
            A string with the profile id, slug, and full name.
        """
        return (
            f"<Profile(id={self.id}, slug='{self.slug}', full_name='{self.full_name}')>"
        )


class ProfileSkills(Base):
    """Links profiles to skills with proficiency details.

    Attributes:
        id: Primary key identifier.
        profile_id: Foreign key to ``Profile.id``.
        skill_id: Foreign key to ``Skill.id``.
        level: Proficiency level for the skill.
        years_of_experience: Years of experience with the skill.
        last_used_at: Date when the skill was last used.

    Relationships:
        profile: Associated profile.
        skill: Associated skill.
    """

    __tablename__ = "ProfileSkills"
    __table_args__ = {"schema": "profile"}

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Foreign Keys
    profile_id: Mapped[int] = mapped_column(ForeignKey("profile.Profile.id"), nullable=False)
    skill_id: Mapped[int] = mapped_column(ForeignKey("profile.Skill.id"), nullable=False)

    # Columns
    level: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    years_of_experience: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    last_used_at: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Relationships
    profile: Mapped["Profile"] = relationship(
        "Profile", back_populates="profile_skills"
    )
    skill: Mapped["Skill"] = relationship("Skill", back_populates="profile_skills")

    def __repr__(self) -> str:
        """Return a concise string representation.

        Returns:
            A string with profile id, skill id, and level.
        """
        return f"<ProfileSkills(profile_id={self.profile_id}, skill_id={self.skill_id}, level={self.level})>"
