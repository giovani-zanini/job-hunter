"""Education model for the job-finder application."""

from sqlalchemy import String, Integer, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING, List
from datetime import date

from src.shared.database.sql_client import Base
from src.shared.database.sql_mixins import SoftDeleteMixin

if TYPE_CHECKING:
    from src.modules.profile.features.profile.models import Profile
    from src.modules.profile.features.user.models import User
    from src.modules.profile.features.skill.models import Skill


class Education(Base, SoftDeleteMixin):
    """Education model representing user educational background."""

    __tablename__ = "Education"
    __table_args__ = {"schema": "profile"}

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Foreign Keys
    user_id: Mapped[int] = mapped_column(ForeignKey("profile.User.id"), nullable=False)

    # Columns
    institution_name: Mapped[str] = mapped_column(String(100), nullable=False)
    degree: Mapped[str] = mapped_column(String(25), nullable=False)
    field_of_study: Mapped[str] = mapped_column(String(100), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="educations")

    education_skills: Mapped[List["EducationSkills"]] = relationship(
        "EducationSkills",
        back_populates="education",
        cascade="all, delete-orphan",
    )

    profile_educations: Mapped[List["ProfileEducation"]] = relationship(
        "ProfileEducation",
        back_populates="education",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Education(id={self.id}, degree='{self.degree}', field='{self.field_of_study}')>"


class EducationSkills(Base):
    """Association table linking Education to Skills."""

    __tablename__ = "EducationSkills"
    __table_args__ = {"schema": "profile"}

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Foreign Keys
    education_id: Mapped[int] = mapped_column(
        ForeignKey("profile.Education.id"), nullable=False
    )
    skill_id: Mapped[int] = mapped_column(ForeignKey("profile.Skill.id"), nullable=False)

    # Relationships
    education: Mapped["Education"] = relationship(
        "Education", back_populates="education_skills"
    )
    skill: Mapped["Skill"] = relationship("Skill", back_populates="education_skills")

    def __repr__(self) -> str:
        return f"<EducationSkills(education_id={self.education_id}, skill_id={self.skill_id})>"


class ProfileEducation(Base):
    """Association table linking Profiles to Education."""

    __tablename__ = "ProfileEducation"
    __table_args__ = {"schema": "profile"}

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Foreign Keys
    profile_id: Mapped[int] = mapped_column(ForeignKey("profile.Profile.id"), nullable=False)
    education_id: Mapped[int] = mapped_column(
        ForeignKey("profile.Education.id"), nullable=False
    )

    # Relationships
    profile: Mapped["Profile"] = relationship(
        "Profile", back_populates="profile_educations"
    )
    education: Mapped["Education"] = relationship(
        "Education", back_populates="profile_educations"
    )

    def __repr__(self) -> str:
        return f"<ProfileEducation(profile_id={self.profile_id}, education_id={self.education_id})>"
