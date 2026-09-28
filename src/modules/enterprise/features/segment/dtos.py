"""Pydantic schemas for Segment feature."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class SegmentCreateRequest(BaseModel):
    name: str = Field(..., max_length=100)


class SegmentUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, max_length=100)


class SegmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class SegmentDetailResponse(SegmentResponse):
    deleted_at: Optional[datetime] = None


class SegmentFilterParams(BaseModel):
    name: Optional[str] = Field(None)
    include_deleted: bool = Field(False)
    skip: int = Field(0, ge=0)
    limit: int = Field(20, ge=1, le=100)
