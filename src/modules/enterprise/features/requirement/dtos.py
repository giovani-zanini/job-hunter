"""Pydantic schemas for Requirement feature."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class RequirementCreateRequest(BaseModel):
    skill: str = Field(..., max_length=50)


class RequirementUpdateRequest(BaseModel):
    skill: Optional[str] = Field(None, max_length=50)


class RequirementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    skill: str


class RequirementDetailResponse(RequirementResponse):
    deleted_at: Optional[datetime] = None


class RequirementFilterParams(BaseModel):
    skill: Optional[str] = Field(None)
    include_deleted: bool = Field(False)
    skip: int = Field(0, ge=0)
    limit: int = Field(20, ge=1, le=100)
