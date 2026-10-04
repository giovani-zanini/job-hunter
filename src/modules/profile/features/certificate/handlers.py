"""Certificate use cases."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.profile.features.certificate import dtos
from src.modules.profile.features.certificate import services
from src.modules.profile.features.certificate.models import (
    Certificate,
    CertificateSkills,
)
from src.modules.profile.features.skill.models import Skill
from src.modules.profile.features.skill.services import ensure_skills_exist
from src.shared import services as shared_services
from src.shared import dtos as shared_dtos


async def create_certificate(
    session: AsyncSession, user_id: int, data: dtos.CertificateCreateRequest
) -> dtos.CertificateDetailResponse:
    """Execute the create certificate use case."""

    # Validate skills exist
    await ensure_skills_exist(session, data.skill_ids)

    # Create certificate
    certificate = await services.create_certificate(
        session=session,
        user_id=user_id,
        name=data.name,
        issuer=data.issuer,
        issue_date=data.issue_date,
        expiration_date=data.expiration_date,
        credential_url=data.credential_url,
    )

    # Add skills
    for skill_id in data.skill_ids:
        await services.add_certificate_skill(session, certificate.id, skill_id)

    await session.refresh(certificate)

    return dtos.CertificateDetailResponse.model_validate(certificate)


async def delete_certificate(
    session: AsyncSession, certificate_id: int, hard_delete: bool = False
) -> dtos.CertificateResponse:
    """Execute the delete certificate use case."""

    # Find certificate
    certificate = await shared_services.ensure_exists(
        session,
        Certificate,
        certificate_id,
        include_deleted=True,
        label="Certificate",
    )


    if hard_delete:
        response = dtos.CertificateResponse.model_validate(certificate)
        await services.delete_certificate(session, certificate, hard_delete=True)

        return response

    certificate = await services.delete_certificate(
        session, certificate, hard_delete=False
    )

    await session.refresh(certificate)

    return dtos.CertificateResponse.model_validate(certificate)


async def get_certificate(
    session: AsyncSession, certificate_id: int, include_deleted: bool = False
) -> dtos.CertificateDetailResponse:
    """Execute the get certificate use case."""

    # Find certificate
    certificate = await shared_services.ensure_exists(
        session,
        Certificate,
        certificate_id,
        include_deleted=include_deleted,
        label="Certificate",
    )

    return dtos.CertificateDetailResponse.model_validate(certificate)


async def list_certificates(
    session: AsyncSession, filters: dtos.CertificateFilterParams
) -> list[dtos.CertificateResponse]:
    """Execute the list certificates use case."""

    certificates = await services.get_all_certificates(
        session=session,
        skip=filters.skip,
        limit=filters.limit,
        user_id=filters.user_id,
        name_filter=filters.name,
        issuer_filter=filters.issuer,
        include_deleted=filters.include_deleted,
    )
    return [dtos.CertificateResponse.model_validate(cert) for cert in certificates]


async def update_certificate(
    session: AsyncSession,
    certificate_id: int,
    data: dtos.CertificateUpdateRequest,
) -> dtos.CertificateResponse:
    """Execute the update certificate use case."""

    # Find certificate
    certificate = await shared_services.ensure_exists(
        session, Certificate, certificate_id, label="Certificate"
    )


    # Update certificate
    certificate = await services.update_certificate(
        session=session,
        certificate=certificate,
        name=data.name,
        issuer=data.issuer,
        issue_date=data.issue_date,
        expiration_date=data.expiration_date,
        credential_url=data.credential_url,
    )

    await session.refresh(certificate)

    return dtos.CertificateResponse.model_validate(certificate)


async def add_certificate_skill(
    session: AsyncSession, certificate_id: int, skill_id: int
) -> shared_dtos.Message:
    """Execute the add certificate skill use case."""

    # Validate certificate exists
    await shared_services.ensure_exists(
        session, Certificate, certificate_id, label="Certificate"
    )

    # Validate skill exists
    await shared_services.ensure_exists(session, Skill, skill_id, label="Skill")

    # Check if association already exists
    await shared_services.ensure_association(
        session,
        CertificateSkills,
        shared_dtos.Association(
            left_field_name="certificate_id",
            left_field_value=certificate_id,
            right_field_name="skill_id",
            right_field_value=skill_id,
            left_label="Certificate",
            right_label="Skill",
        ),
        type="absent",
    )

    # Create association
    await services.add_certificate_skill(session, certificate_id, skill_id)

    return shared_dtos.Message(
        message="Skill added to certificate.",
        meta={"skill_id": skill_id, "certificate_id": certificate_id},
    )


async def remove_certificate_skill(
    session: AsyncSession, certificate_id: int, skill_id: int
) -> None:
    """Execute the remove certificate skill use case."""

    # Find association
    cert_skill = await shared_services.ensure_association(
        session,
        CertificateSkills,
        shared_dtos.Association(
            left_field_name="certificate_id",
            left_field_value=certificate_id,
            right_field_name="skill_id",
            right_field_value=skill_id,
            left_label="Certificate",
            right_label="Skill",
        ),
        type="present",
    )

    # Remove association
    await services.remove_certificate_skill(session, cert_skill)
