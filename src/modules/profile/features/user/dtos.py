"""Schemas for local profile owners."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_anonymous: bool


class UserDetailResponse(UserResponse):
    deleted_at: Optional[datetime] = None


class UserFilterParams(BaseModel):
    is_anonymous: Optional[bool] = Field(None, description="Filter anonymous owner")
    include_deleted: bool = Field(False, description="Include soft deleted users")
    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(20, ge=1, le=100, description="Maximum number of records")
