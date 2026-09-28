"""Certificate service for database operations."""

from datetime import date
from typing import Optional, Sequence

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.profile.features.certificate.models import Certificate, CertificateSkills
from src.shared import services as shared_services


async def get_certificate_by_id(
    session: AsyncSession, certificate_id: int, include_deleted: bool = False
) -> Optional[Certificate]:
    """Get a certificate by ID."""
    return await shared_services.get_one_by_field(
        session, Certificate, "id", certificate_id, include_deleted
    )


async def get_all_certificates(
    session: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    user_id: Optional[int] = None,
    name_filter: Optional[str] = None,
    issuer_filter: Optional[str] = None,
    include_deleted: bool = False,
) -> Sequence[Certificate]:
    """Get all certificates with optional filters."""
    stmt = select(Certificate)

    if not include_deleted:
        stmt = stmt.where(Certificate.deleted_at.is_(None))

    if user_id:
        stmt = stmt.where(Certificate.user_id == user_id)

    if name_filter:
        stmt = stmt.where(Certificate.name.ilike(f"%{name_filter}%"))

    if issuer_filter:
        stmt = stmt.where(Certificate.issuer.ilike(f"%{issuer_filter}%"))

    stmt = stmt.offset(skip).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()


async def count_certificates(
    session: AsyncSession,
    user_id: Optional[int] = None,
    name_filter: Optional[str] = None,
    issuer_filter: Optional[str] = None,
    include_deleted: bool = False,
) -> int:
    """Count certificates with optional filters."""
    stmt = select(func.count(Certificate.id))

    if not include_deleted:
        stmt = stmt.where(Certificate.deleted_at.is_(None))

    if user_id:
        stmt = stmt.where(Certificate.user_id == user_id)

    if name_filter:
        stmt = stmt.where(Certificate.name.ilike(f"%{name_filter}%"))

    if issuer_filter:
        stmt = stmt.where(Certificate.issuer.ilike(f"%{issuer_filter}%"))

    result = await session.execute(stmt)
    return result.unique().scalar_one()


async def create_certificate(
    session: AsyncSession,
    user_id: int,
    name: str,
    issuer: str,
    issue_date: date,
    expiration_date: Optional[date] = None,
    credential_url: Optional[str] = None,
) -> Certificate:
    """Create a new certificate."""
    return await shared_services.create(
        session,
        Certificate,
        user_id=user_id,
        name=name,
        issuer=issuer,
        issue_date=issue_date,
        expiration_date=expiration_date,
        credential_url=credential_url,
    )


async def update_certificate(
    session: AsyncSession,
    certificate: Certificate,
    name: Optional[str] = None,
    issuer: Optional[str] = None,
    issue_date: Optional[date] = None,
    expiration_date: Optional[date] = None,
    credential_url: Optional[str] = None,
) -> Certificate:
    """Update certificate fields."""
    if name is not None:
        certificate.name = name
    if issuer is not None:
        certificate.issuer = issuer
    if issue_date is not None:
        certificate.issue_date = issue_date
    if expiration_date is not None:
        certificate.expiration_date = expiration_date
    if credential_url is not None:
        certificate.credential_url = credential_url
    await session.flush()
    return certificate


async def delete_certificate(
    session: AsyncSession, certificate: Certificate, hard_delete: bool = False
) -> Certificate:
    """Delete a certificate (soft or hard delete)."""
    return await shared_services.delete(session, certificate, hard_delete)


# --- Skill Association Functions ---


async def add_certificate_skill(
    session: AsyncSession, certificate_id: int, skill_id: int
) -> CertificateSkills:
    """Add a skill to a certificate."""
    return await shared_services.create(
        session, CertificateSkills, certificate_id=certificate_id, skill_id=skill_id
    )


async def get_certificate_skill(
    session: AsyncSession, certificate_id: int, skill_id: int
) -> Optional[CertificateSkills]:
    """Get a specific certificate-skill association."""
    stmt = select(CertificateSkills).where(
        CertificateSkills.certificate_id == certificate_id,
        CertificateSkills.skill_id == skill_id,
    )
    result = await session.execute(stmt)
    return result.unique().scalar_one_or_none()


async def remove_certificate_skill(
    session: AsyncSession, cert_skill: CertificateSkills
) -> None:
    """Remove a skill from a certificate."""
    await session.delete(cert_skill)
    await session.flush()
