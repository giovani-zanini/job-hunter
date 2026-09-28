"""Pydantic schemas for Location feature."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class LocationCreateRequest(BaseModel):
    country: str = Field(..., max_length=4, description="ISO country code (e.g. BRA)")
    state: str = Field(..., max_length=25)
    city: Optional[str] = Field(None, max_length=50)
    neighborhood: Optional[str] = Field(None, max_length=64)
    postal_code: Optional[str] = Field(None, max_length=16)
    street: Optional[str] = Field(None, max_length=150)
    number: Optional[str] = Field(None, max_length=15)
    complement: Optional[str] = Field(None, max_length=25)


class LocationUpdateRequest(BaseModel):
    country: Optional[str] = Field(None, max_length=4)
    state: Optional[str] = Field(None, max_length=25)
    city: Optional[str] = Field(None, max_length=50)
    neighborhood: Optional[str] = Field(None, max_length=64)
    postal_code: Optional[str] = Field(None, max_length=16)
    street: Optional[str] = Field(None, max_length=150)
    number: Optional[str] = Field(None, max_length=15)
    complement: Optional[str] = Field(None, max_length=25)


class LocationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    country: str
    state: str
    city: Optional[str] = None
    neighborhood: Optional[str] = None
    postal_code: Optional[str] = None
    street: Optional[str] = None
    number: Optional[str] = None
    complement: Optional[str] = None


class LocationDetailResponse(LocationResponse):
    deleted_at: Optional[datetime] = None


class LocationFilterParams(BaseModel):
    country: Optional[str] = Field(None)
    state: Optional[str] = Field(None)
    city: Optional[str] = Field(None)
    include_deleted: bool = Field(False)
    skip: int = Field(0, ge=0)
    limit: int = Field(20, ge=1, le=100)
