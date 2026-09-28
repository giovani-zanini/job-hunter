"""Pydantic schemas for Experience feature."""

from datetime import date, datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field


# --- Nested Schemas ---


class AchievementInput(BaseModel):
    """Schema for creating an achievement."""

    title: str = Field(..., max_length=64, description="Achievement title")
    description: str = Field(..., description="Achievement description")


class AchievementResponse(BaseModel):
    """Schema for achievement response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    experience_id: int
    title: str
    description: str


class AchievementUpdateRequest(BaseModel):
    """Schema for updating an achievement."""

    title: Optional[str] = Field(None, max_length=64, description="Achievement title")
    description: Optional[str] = Field(None, description="Achievement description")


class ExperienceSkillInput(BaseModel):
    """Schema for associating a skill with an experience."""

    skill_id: int = Field(..., description="Skill ID")


# --- Request Schemas ---


class ExperienceCreateRequest(BaseModel):
    """Schema for creating a new experience."""

    company_id: int = Field(..., description="Company ID")
    position_title: str = Field(..., max_length=100, description="Position/job title")
    start_date: date = Field(..., description="Start date")
    end_date: Optional[date] = Field(None, description="End date (null if current)")
    description: str = Field(..., description="Job description")
    achievements: List[AchievementInput] = Field(default=[], description="Achievements")
    skill_ids: List[int] = Field(default=[], description="Skill IDs to associate")


class ExperienceUpdateRequest(BaseModel):
    """Schema for updating an experience."""

    company_id: Optional[int] = Field(None, description="Company ID")
    position_title: Optional[str] = Field(
        None, max_length=100, description="Position/job title"
    )
    start_date: Optional[date] = Field(None, description="Start date")
    end_date: Optional[date] = Field(None, description="End date")
    description: Optional[str] = Field(None, description="Job description")


# --- Response Schemas ---


class ExperienceResponse(BaseModel):
    """Schema for experience response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    company_id: int
    position_title: str
    start_date: date
    end_date: Optional[date] = None
    description: str


class ExperienceDetailResponse(BaseModel):
    """Schema for detailed experience response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    company_id: int
    position_title: str
    start_date: date
    end_date: Optional[date] = None
    description: str
    deleted_at: Optional[datetime] = None
    achievements: List[AchievementResponse] = []


# --- Filter Schemas ---


class ExperienceFilterParams(BaseModel):
    """Schema for experience list filters."""

    user_id: Optional[int] = Field(None, description="Filter by user ID")
    company_id: Optional[int] = Field(None, description="Filter by company ID")
    position_title: Optional[str] = Field(
        None, description="Filter by position title (partial match)"
    )
    include_deleted: bool = Field(False, description="Include soft deleted experiences")
    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(
        20, ge=1, le=100, description="Maximum number of records to return"
    )
