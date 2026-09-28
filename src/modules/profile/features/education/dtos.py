"""Pydantic schemas for Education feature."""

from datetime import date, datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field


# --- Request Schemas ---


class EducationCreateRequest(BaseModel):
    """Schema for creating a new education."""

    institution_name: str = Field(..., max_length=100, description="Institution name")
    degree: str = Field(..., max_length=25, description="Degree type")
    field_of_study: str = Field(..., max_length=100, description="Field of study")
    start_date: date = Field(..., description="Start date")
    end_date: date = Field(..., description="End date")
    skill_ids: List[int] = Field(default=[], description="Skill IDs to associate")


class EducationUpdateRequest(BaseModel):
    """Schema for updating an education."""

    institution_name: Optional[str] = Field(
        None, max_length=100, description="Institution name"
    )
    degree: Optional[str] = Field(None, max_length=25, description="Degree type")
    field_of_study: Optional[str] = Field(
        None, max_length=100, description="Field of study"
    )
    start_date: Optional[date] = Field(None, description="Start date")
    end_date: Optional[date] = Field(None, description="End date")


# --- Response Schemas ---


class EducationResponse(BaseModel):
    """Schema for education response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    institution_name: str
    degree: str
    field_of_study: str
    start_date: date
    end_date: date


class EducationDetailResponse(BaseModel):
    """Schema for detailed education response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    institution_name: str
    degree: str
    field_of_study: str
    start_date: date
    end_date: date
    deleted_at: Optional[datetime] = None


# --- Filter Schemas ---


class EducationFilterParams(BaseModel):
    """Schema for education list filters."""

    user_id: Optional[int] = Field(None, description="Filter by user ID")
    institution_name: Optional[str] = Field(
        None, description="Filter by institution (partial match)"
    )
    degree: Optional[str] = Field(None, description="Filter by degree (partial match)")
    field_of_study: Optional[str] = Field(
        None, description="Filter by field (partial match)"
    )
    include_deleted: bool = Field(False, description="Include soft deleted education")
    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(
        20, ge=1, le=100, description="Maximum number of records to return"
    )
