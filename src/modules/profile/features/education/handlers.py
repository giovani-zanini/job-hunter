"""Education use cases."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.profile.features.education import dtos
from src.modules.profile.features.education import services
from src.modules.profile.features.education.models import Education, EducationSkills
from src.modules.profile.features.skill.models import Skill
from src.modules.profile.features.skill.services import ensure_skills_exist
from src.shared import services as shared_services
from src.shared import dtos as shared_dtos


async def create_education(
    session: AsyncSession, user_id: int, data: dtos.EducationCreateRequest
) -> dtos.EducationDetailResponse:
    """Execute the create education use case."""

    # Validate skills exist
    await ensure_skills_exist(session, data.skill_ids)

    # Create education
    education = await services.create_education(
        session=session,
        user_id=user_id,
        institution_name=data.institution_name,
        degree=data.degree,
        field_of_study=data.field_of_study,
        start_date=data.start_date,
        end_date=data.end_date,
    )

    # Add skills
    for skill_id in data.skill_ids:
        await services.add_education_skill(session, education.id, skill_id)

    await session.refresh(education)

    return dtos.EducationDetailResponse.model_validate(education)


async def delete_education(
    session: AsyncSession, education_id: int, hard_delete: bool = False
) -> dtos.EducationResponse:
    """Execute the delete education use case."""

    # Find education
    education = await shared_services.ensure_exists(
        session, Education, education_id, include_deleted=True, label="Education"
    )


    if hard_delete:
        response = dtos.EducationResponse.model_validate(education)
        await services.delete_education(session, education, hard_delete=True)

        return response

    education = await services.delete_education(session, education, hard_delete=False)

    await session.refresh(education)

    return dtos.EducationResponse.model_validate(education)


async def get_education(
    session: AsyncSession, education_id: int, include_deleted: bool = False
) -> dtos.EducationDetailResponse:
    """Execute the get education use case."""

    # Find education
    education = await shared_services.ensure_exists(
        session,
        Education,
        education_id,
        include_deleted=include_deleted,
        label="Education",
    )

    return dtos.EducationDetailResponse.model_validate(education)


async def list_education(
    session: AsyncSession, filters: dtos.EducationFilterParams
) -> list[dtos.EducationResponse]:
    """Execute the list education use case."""

    education_list = await services.get_all_education(
        session=session,
        skip=filters.skip,
        limit=filters.limit,
        user_id=filters.user_id,
        institution_name_filter=filters.institution_name,
        degree_filter=filters.degree,
        field_of_study_filter=filters.field_of_study,
        include_deleted=filters.include_deleted,
    )
    return [dtos.EducationResponse.model_validate(edu) for edu in education_list]


async def update_education(
    session: AsyncSession,
    education_id: int,
    data: dtos.EducationUpdateRequest,
) -> dtos.EducationResponse:
    """Execute the update education use case."""

    # Find education
    education = await shared_services.ensure_exists(
        session, Education, education_id, label="Education"
    )


    # Update education
    education = await services.update_education(
        session=session,
        education=education,
        institution_name=data.institution_name,
        degree=data.degree,
        field_of_study=data.field_of_study,
        start_date=data.start_date,
        end_date=data.end_date,
    )

    await session.refresh(education)

    return dtos.EducationResponse.model_validate(education)


async def add_education_skill(
    session: AsyncSession, education_id: int, skill_id: int
) -> shared_dtos.Message:
    """Execute the add education skill use case."""

    # Validate education exists
    await shared_services.ensure_exists(
        session, Education, education_id, label="Education"
    )

    # Validate skill exists
    await shared_services.ensure_exists(session, Skill, skill_id, label="Skill")

    # Check if association already exists
    await shared_services.ensure_association(
        session,
        EducationSkills,
        shared_dtos.Association(
            left_field_name="education_id",
            left_field_value=education_id,
            right_field_name="skill_id",
            right_field_value=skill_id,
            left_label="Education",
            right_label="Skill",
        ),
        type="absent",
    )

    # Create association
    await services.add_education_skill(session, education_id, skill_id)

    return shared_dtos.Message(
        message="Skill added to education.",
        meta={"skill_id": skill_id, "education_id": education_id},
    )


async def remove_education_skill(
    session: AsyncSession, education_id: int, skill_id: int
) -> None:
    """Execute the remove education skill use case."""

    # Find association
    edu_skill = await shared_services.ensure_association(
        session,
        EducationSkills,
        shared_dtos.Association(
            left_field_name="education_id",
            left_field_value=education_id,
            right_field_name="skill_id",
            right_field_value=skill_id,
            left_label="Education",
            right_label="Skill",
        ),
        type="present",
    )

    # Remove association
    await services.remove_education_skill(session, edu_skill)
