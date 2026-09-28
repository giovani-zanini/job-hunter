"""Certificate model for the job-finder application."""

from sqlalchemy import String, Integer, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING, List, Optional
from datetime import date

from src.shared.database.sql_client import Base
from src.shared.database.sql_mixins import SoftDeleteMixin

if TYPE_CHECKING:
    from src.modules.profile.features.user.models import User
    from src.modules.profile.features.skill.models import Skill


class Certificate(Base, SoftDeleteMixin):
    """Certificate model representing user professional certifications."""

    __tablename__ = "Certificate"
    __table_args__ = {"schema": "profile"}

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Foreign Keys
    user_id: Mapped[int] = mapped_column(ForeignKey("profile.User.id"), nullable=False)

    # Columns
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    issuer: Mapped[str] = mapped_column(String(100), nullable=False)
    issue_date: Mapped[date] = mapped_column(Date, nullable=False)
    expiration_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    credential_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="certificates")

    certificate_skills: Mapped[List["CertificateSkills"]] = relationship(
        "CertificateSkills",
        back_populates="certificate",
        cascade="all, delete-orphan",
    )

    profile_certificates: Mapped[List["ProfileCertificate"]] = relationship(
        "ProfileCertificate",
        back_populates="certificate",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<Certificate(id={self.id}, name='{self.name}', issuer='{self.issuer}')>"
        )


class CertificateSkills(Base):
    """Association table linking Certificates to Skills."""

    __tablename__ = "CertificateSkills"
    __table_args__ = {"schema": "profile"}

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Foreign Keys
    certificate_id: Mapped[int] = mapped_column(
        ForeignKey("profile.Certificate.id"), nullable=False
    )
    skill_id: Mapped[int] = mapped_column(ForeignKey("profile.Skill.id"), nullable=False)

    # Relationships
    certificate: Mapped["Certificate"] = relationship(
        "Certificate", back_populates="certificate_skills"
    )
    skill: Mapped["Skill"] = relationship("Skill", back_populates="certificate_skills")

    def __repr__(self) -> str:
        return f"<CertificateSkills(certificate_id={self.certificate_id}, skill_id={self.skill_id})>"


class ProfileCertificate(Base):
    """Association table linking Profiles to Certificates."""

    __tablename__ = "ProfileCertificate"
    __table_args__ = {"schema": "profile"}

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Foreign Keys
    profile_id: Mapped[int] = mapped_column(ForeignKey("profile.Profile.id"), nullable=False)
    certificate_id: Mapped[int] = mapped_column(
        ForeignKey("profile.Certificate.id"), nullable=False
    )

    # Relationships
    profile: Mapped["Profile"] = relationship(
        "Profile", back_populates="profile_certificates"
    )
    certificate: Mapped["Certificate"] = relationship(
        "Certificate", back_populates="profile_certificates"
    )

    def __repr__(self) -> str:
        return f"<ProfileCertificate(profile_id={self.profile_id}, certificate_id={self.certificate_id})>"
