"""Experience model for the job-finder application."""

from sqlalchemy import String, Integer, Text, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING, List, Optional
from datetime import date

from src.shared.database.sql_client import Base
from src.shared.database.sql_mixins import SoftDeleteMixin

if TYPE_CHECKING:
    from src.modules.profile.features.company.models import Company
    from src.modules.profile.features.user.models import User
    from src.modules.profile.features.skill.models import Skill


class Experience(Base, SoftDeleteMixin):
    """Experience model representing user work experience."""

    __tablename__ = "Experience"
    __table_args__ = {"schema": "profile"}

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Foreign Keys
    company_id: Mapped[int] = mapped_column(ForeignKey("profile.Company.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("profile.User.id"), nullable=False)

    # Columns
    position_title: Mapped[str] = mapped_column(String(100), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationships
    company: Mapped["Company"] = relationship("Company", back_populates="experiences")
    user: Mapped["User"] = relationship("User", back_populates="experiences")

    achievements: Mapped[List["Achievements"]] = relationship(
        "Achievements",
        back_populates="experience",
        cascade="all, delete-orphan",
    )

    experience_skills: Mapped[List["ExperienceSkills"]] = relationship(
        "ExperienceSkills",
        back_populates="experience",
        cascade="all, delete-orphan",
    )

    profile_experiences: Mapped[List["ProfileExperience"]] = relationship(
        "ProfileExperience",
        back_populates="experience",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Experience(id={self.id}, position='{self.position_title}', company_id={self.company_id})>"


class Achievements(Base, SoftDeleteMixin):
    """Achievements model representing accomplishments within an experience."""

    __tablename__ = "Achievements"
    __table_args__ = {"schema": "profile"}

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Foreign Keys
    experience_id: Mapped[int] = mapped_column(
        ForeignKey("profile.Experience.id"), nullable=False
    )

    # Columns
    title: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationships
    experience: Mapped["Experience"] = relationship(
        "Experience", back_populates="achievements"
    )

    def __repr__(self) -> str:
        return f"<Achievements(id={self.id}, title='{self.title}')>"


class ExperienceSkills(Base):
    """Association table linking Experiences to Skills."""

    __tablename__ = "ExperienceSkills"
    __table_args__ = {"schema": "profile"}

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Foreign Keys
    skill_id: Mapped[int] = mapped_column(ForeignKey("profile.Skill.id"), nullable=False)
    experience_id: Mapped[int] = mapped_column(
        ForeignKey("profile.Experience.id"), nullable=False
    )

    # Relationships
    skill: Mapped["Skill"] = relationship("Skill", back_populates="experience_skills")
    experience: Mapped["Experience"] = relationship(
        "Experience", back_populates="experience_skills"
    )

    def __repr__(self) -> str:
        return f"<ExperienceSkills(experience_id={self.experience_id}, skill_id={self.skill_id})>"


class ProfileExperience(Base):
    """Association table linking Profiles to Experiences."""

    __tablename__ = "ProfileExperience"
    __table_args__ = {"schema": "profile"}

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Foreign Keys
    profile_id: Mapped[int] = mapped_column(ForeignKey("profile.Profile.id"), nullable=False)
    experience_id: Mapped[int] = mapped_column(
        ForeignKey("profile.Experience.id"), nullable=False
    )

    # Relationships
    profile: Mapped["Profile"] = relationship(
        "Profile", back_populates="profile_experiences"
    )
    experience: Mapped["Experience"] = relationship(
        "Experience", back_populates="profile_experiences"
    )

    def __repr__(self) -> str:
        return f"<ProfileExperience(profile_id={self.profile_id}, experience_id={self.experience_id})>"
