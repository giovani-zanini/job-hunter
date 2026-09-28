"""Pydantic schemas for User feature (auth module)."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# --- Request Schemas ---


class UserCreateRequest(BaseModel):
    """Schema for creating a new user with credentials."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(
        ..., min_length=8, max_length=128, description="User password"
    )


class UserUpdateRequest(BaseModel):
    """Schema for updating a user."""

    email: Optional[EmailStr] = Field(None, description="User email address")
    is_active: Optional[bool] = Field(None, description="Whether the user is active")
    is_verified: Optional[bool] = Field(
        None, description="Whether the user is verified"
    )


# --- Response Schemas ---


class UserResponse(BaseModel):
    """Schema for user response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime | None = None


# --- Filter Schemas ---


class UserFilterParams(BaseModel):
    """Schema for user list filters."""

    email: Optional[str] = Field(None, description="Filter by email (partial match)")
    role_id: Optional[int] = Field(None, description="Filter by role ID")
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(
        20, ge=1, le=100, description="Maximum number of records to return"
    )
