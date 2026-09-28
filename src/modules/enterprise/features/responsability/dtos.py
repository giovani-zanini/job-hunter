"""Pydantic schemas for Responsability feature."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ResponsabilityCreateRequest(BaseModel):
    action: str = Field(..., max_length=50)
    target: str = Field(..., max_length=50)
    outcome: str = Field(..., max_length=50)


class ResponsabilityUpdateRequest(BaseModel):
    action: Optional[str] = Field(None, max_length=50)
    target: Optional[str] = Field(None, max_length=50)
    outcome: Optional[str] = Field(None, max_length=50)


class ResponsabilityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    action: str
    target: str
    outcome: str


class ResponsabilityDetailResponse(ResponsabilityResponse):
    deleted_at: Optional[datetime] = None


class ResponsabilityFilterParams(BaseModel):
    action: Optional[str] = Field(None)
    include_deleted: bool = Field(False)
    skip: int = Field(0, ge=0)
    limit: int = Field(20, ge=1, le=100)
