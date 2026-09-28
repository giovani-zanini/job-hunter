"""Pydantic schemas for Profile feature.

This module provides data transfer objects (DTOs) for the Profile feature,
organized into four main categories:

    - Nested Association Schemas: For managing relationships between profiles
      and other entities (skills, links, experiences, education, certificates).
    - Request Schemas: For API request payloads (create, update, add/update skills).
    - Response Schemas: For API response payloads (profile data, detail view).
    - Filter Schemas: For query filtering and pagination parameters.

All schemas use Pydantic's BaseModel for validation and serialization.
Some schemas include model_config with from_attributes=True for ORM compatibility.
"""

from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from src.modules.profile.features.skill.dtos import SkillResponse


# --- Nested Association Schemas ---


class ProfileSkillInput(BaseModel):
    """Schema for adding a skill to a profile.

    Used to associate a skill with a profile, including proficiency level
    and years of experience. Validates skill existence and proficiency constraints.

    Attributes:
        skill_id (int): The ID of the skill to associate with the profile.
        level (int): Proficiency level on a scale of 1-5, where 1 is beginner
            and 5 is expert.
        years_of_experience (int): Total years of experience with this skill.
            Must be non-negative.
        last_used_at (Optional[date]): The most recent date the skill was used.
            If not provided, defaults to None.
    """

    skill_id: int = Field(..., description="Skill ID")
    level: int = Field(..., ge=1, le=5, description="Proficiency level (1-5)")
    years_of_experience: int = Field(..., ge=0, description="Years of experience")
    last_used_at: Optional[date] = Field(None, description="Last time skill was used")


class ProfileSkillResponse(BaseModel):
    """Schema for profile skill response.

    Represents a skill associated with a profile, including its relationship data
    and the nested skill object. Used in profile detail responses.

    Attributes:
        id (int): The unique identifier of the profile-skill association.
        skill_id (int): The ID of the associated skill.
        level (int): Proficiency level (1-5 scale).
        years_of_experience (int): Total years of experience with this skill.
        last_used_at (Optional[date]): The most recent date the skill was used.
        skill (Optional[SkillResponse]): The full skill object details, if included
            in the response through eager loading.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    skill_id: int
    level: int
    years_of_experience: int
    last_used_at: Optional[date] = None
    skill: Optional[SkillResponse] = None


class ProfileLinkInput(BaseModel):
    """Schema for associating a link to a profile.

    Used in API requests to add an existing link to a profile.

    Attributes:
        link_id (int): The ID of the link to associate with the profile.
    """

    link_id: int = Field(..., description="Link ID")


class ProfileExperienceInput(BaseModel):
    """Schema for associating an experience to a profile.

    Used in API requests to add an existing experience record to a profile.

    Attributes:
        experience_id (int): The ID of the experience to associate with the profile.
    """

    experience_id: int = Field(..., description="Experience ID")


class ProfileEducationInput(BaseModel):
    """Schema for associating an education to a profile.

    Used in API requests to add an existing education record to a profile.

    Attributes:
        education_id (int): The ID of the education record to associate with
            the profile.
    """

    education_id: int = Field(..., description="Education ID")


class ProfileCertificateInput(BaseModel):
    """Schema for associating a certificate to a profile.

    Used in API requests to add an existing certificate to a profile.

    Attributes:
        certificate_id (int): The ID of the certificate to associate with
            the profile.
    """

    certificate_id: int = Field(..., description="Certificate ID")


# --- Request Schemas ---


class ProfileCreateRequest(BaseModel):
    """Schema for creating a new profile.

    Used in POST requests to create a new profile for a user. All fields are
    required. The slug must be unique per user and is used in profile URLs.

    Attributes:
        user_id (int): The ID of the user who owns this profile.
        slug (str): URL-friendly identifier for the profile, maximum 25 characters.
        full_name (str): User's full name, maximum 150 characters.
        title (str): Professional title or job role, maximum 125 characters.
        bio (str): Professional biography or personal description.
    """

    slug: str = Field(..., max_length=25, description="Profile URL slug")
    full_name: str = Field(..., max_length=150, description="Full name")
    title: str = Field(..., max_length=125, description="Professional title")
    bio: str = Field(..., description="Bio/description")


class ProfileUpdateRequest(BaseModel):
    """Schema for updating a profile.

    Used in PATCH/PUT requests to update an existing profile. All fields are
    optional, allowing partial updates. Only provided fields will be modified.

    Attributes:
        slug (Optional[str]): New URL-friendly identifier, maximum 25 characters.
        full_name (Optional[str]): Updated full name, maximum 150 characters.
        title (Optional[str]): Updated professional title, maximum 125 characters.
        bio (Optional[str]): Updated professional biography or description.
    """

    slug: Optional[str] = Field(None, max_length=25, description="Profile URL slug")
    full_name: Optional[str] = Field(None, max_length=150, description="Full name")
    title: Optional[str] = Field(None, max_length=125, description="Professional title")
    bio: Optional[str] = Field(None, description="Bio/description")


class ProfileAddSkillRequest(BaseModel):
    """Schema for adding a skill to a profile.

    Used in POST requests to associate a skill with a profile. Includes
    proficiency level and experience metadata.

    Attributes:
        skill_id (int): The ID of the skill to add to the profile.
        level (int): Proficiency level on a scale of 1-5.
        years_of_experience (int): Total years of experience with this skill.
            Must be non-negative.
        last_used_at (Optional[date]): The most recent date the skill was used.
    """

    skill_id: int = Field(..., description="Skill ID")
    level: int = Field(..., ge=1, le=5, description="Proficiency level (1-5)")
    years_of_experience: int = Field(..., ge=0, description="Years of experience")
    last_used_at: Optional[date] = Field(None, description="Last time skill was used")


class ProfileUpdateSkillRequest(BaseModel):
    """Schema for updating a profile skill.

    Used in PATCH/PUT requests to update an existing profile-skill association.
    All fields are optional for partial updates.

    Attributes:
        level (Optional[int]): Updated proficiency level (1-5 scale).
        years_of_experience (Optional[int]): Updated years of experience with
            the skill. Must be non-negative if provided.
        last_used_at (Optional[date]): Updated most recent usage date.
    """

    level: Optional[int] = Field(
        None, ge=1, le=5, description="Proficiency level (1-5)"
    )
    years_of_experience: Optional[int] = Field(
        None, ge=0, description="Years of experience"
    )
    last_used_at: Optional[date] = Field(None, description="Last time skill was used")


# --- Response Schemas ---


class ProfileResponse(BaseModel):
    """Schema for profile response.

    Represents a basic profile response containing core profile information.
    Used in list endpoints and basic profile retrieval responses.

    Attributes:
        id (int): The unique identifier of the profile.
        user_id (int): The ID of the user who owns this profile.
        slug (str): URL-friendly identifier for the profile.
        full_name (str): User's full name.
        title (str): Professional title or job role.
        bio (str): Professional biography or personal description.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    slug: str
    full_name: str
    title: str
    bio: str


class ProfileDetailResponse(BaseModel):
    """Schema for detailed profile response.

    Represents a comprehensive profile response with extended information.
    Currently mirrors ProfileResponse but is prepared for future inclusion of
    nested data such as skills, links, experiences, education, and certificates.
    Used in profile detail endpoints (GET /profiles/{id}).

    Future Fields (to be added):
        skills: List of associated ProfileSkillResponse objects.
        links: List of associated ProfileLinkResponse objects.
        experiences: List of associated ProfileExperienceResponse objects.
        education: List of associated ProfileEducationResponse objects.
        certificates: List of associated ProfileCertificateResponse objects.

    Attributes:
        id (int): The unique identifier of the profile.
        user_id (int): The ID of the user who owns this profile.
        slug (str): URL-friendly identifier for the profile.
        full_name (str): User's full name.
        title (str): Professional title or job role.
        bio (str): Professional biography or personal description.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    slug: str
    full_name: str
    title: str
    bio: str


# --- Filter Schemas ---


class ProfileFilterParams(BaseModel):
    """Schema for profile list filters.

    Used in GET requests to filter and paginate profile results. Supports partial
    text matching for slug and full_name fields. Implements cursor-based pagination
    with skip/limit parameters.

    Attributes:
        user_id (Optional[int]): Filter profiles by user ID. If provided, only
            profiles belonging to this user are returned.
        slug (Optional[str]): Filter profiles by slug using partial string matching.
            Case-sensitive matching is applied.
        full_name (Optional[str]): Filter profiles by full name using partial string
            matching. Case-sensitive matching is applied.
        include_deleted (bool): Include soft-deleted profiles in results. Defaults
            to False, only active profiles are returned by default.
        skip (int): Number of records to skip from the beginning of the result set.
            Used for pagination. Must be non-negative. Defaults to 0.
        limit (int): Maximum number of records to return in a single response.
            Must be between 1 and 100 inclusive. Defaults to 20.
    """

    user_id: Optional[int] = Field(None, description="Filter by user ID")
    slug: Optional[str] = Field(None, description="Filter by slug (partial match)")
    full_name: Optional[str] = Field(
        None, description="Filter by full name (partial match)"
    )
    include_deleted: bool = Field(False, description="Include soft deleted profiles")
    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(
        20, ge=1, le=100, description="Maximum number of records to return"
    )
