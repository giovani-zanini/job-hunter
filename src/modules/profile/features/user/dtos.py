"""Pydantic schemas for User feature."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# --- Response Schemas ---


class UserResponse(BaseModel):
    """Schema for user response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    external_id: int


class UserDetailResponse(BaseModel):
    """Schema for detailed user response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    external_id: int
    deleted_at: Optional[datetime] = None


# --- Filter Schemas ---


class UserFilterParams(BaseModel):
    """Schema for user list filters."""

    external_id: Optional[int] = Field(
        None, description="Filter by external auth user ID"
    )
    include_deleted: bool = Field(False, description="Include soft deleted users")
    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(
        20, ge=1, le=100, description="Maximum number of records to return"
    )
