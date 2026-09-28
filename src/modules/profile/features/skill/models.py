import enum
from sqlalchemy import String, Integer, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List

from src.shared.database.sql_client import Base
from src.shared.database.sql_mixins import SoftDeleteMixin


class SkillCategory(str, enum.Enum):
    """Enum for skill categories."""

    LANGUAGE = "LANGUAGE"
    TOOL = "TOOL"
    FRAMEWORK = "FRAMEWORK"


class Skill(Base, SoftDeleteMixin):
    """Skill model representing technical and professional skills."""

    __tablename__ = "Skill"
    __table_args__ = {"schema": "profile"}

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Columns
    category: Mapped[SkillCategory] = mapped_column(
        Enum(SkillCategory, name="SKILL_CATEGORY"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    # Relationships
    profile_skills: Mapped[List["ProfileSkills"]] = relationship(
        "ProfileSkills", back_populates="skill", cascade="all, delete-orphan"
    )

    experience_skills: Mapped[List["ExperienceSkills"]] = relationship(
        "ExperienceSkills", back_populates="skill", cascade="all, delete-orphan"
    )

    education_skills: Mapped[List["EducationSkills"]] = relationship(
        "EducationSkills", back_populates="skill", cascade="all, delete-orphan"
    )

    certificate_skills: Mapped[List["CertificateSkills"]] = relationship(
        "CertificateSkills", back_populates="skill", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Skill(id={self.id}, name='{self.name}', category='{self.category.value}')>"
