"""Pydantic schemas for Company / CompanyUnit / CompanySegment features."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


# --- Company ---

class CompanyCreateRequest(BaseModel):
    name: str = Field(..., max_length=150)


class CompanyUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, max_length=150)


class CompanyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class CompanyDetailResponse(CompanyResponse):
    deleted_at: Optional[datetime] = None


class CompanyFilterParams(BaseModel):
    name: Optional[str] = Field(None)
    include_deleted: bool = Field(False)
    skip: int = Field(0, ge=0)
    limit: int = Field(20, ge=1, le=100)


# --- CompanyUnit ---

class CompanyUnitCreateRequest(BaseModel):
    location_id: int = Field(..., description="Location ID")


class CompanyUnitResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_id: int
    location_id: int


# --- CompanySegment ---

class CompanySegmentCreateRequest(BaseModel):
    segment_id: int


class CompanySegmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_id: int
    segment_id: int
