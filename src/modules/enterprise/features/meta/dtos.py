"""Pydantic schemas for Meta feature."""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field


class MetaCreateRequest(BaseModel):
    app_version: str = Field("1.0.0", max_length=25)
    extraction_timestamp: datetime
    parsing_timestamp: datetime
    source_url: str
    custom_data: Optional[Dict[str, Any]] = None
    vacancy_id: Optional[int] = None
    company_id: Optional[int] = None


class MetaUpdateRequest(BaseModel):
    app_version: Optional[str] = Field(None, max_length=25)
    extraction_timestamp: Optional[datetime] = None
    parsing_timestamp: Optional[datetime] = None
    source_url: Optional[str] = None
    custom_data: Optional[Dict[str, Any]] = None
    vacancy_id: Optional[int] = None
    company_id: Optional[int] = None


class MetaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    app_version: str
    extraction_timestamp: datetime
    parsing_timestamp: datetime
    source_url: str
    custom_data: Optional[Dict[str, Any]] = None
    vacancy_id: Optional[int] = None
    company_id: Optional[int] = None


class MetaDetailResponse(MetaResponse):
    deleted_at: Optional[datetime] = None


class MetaFilterParams(BaseModel):
    vacancy_id: Optional[int] = None
    company_id: Optional[int] = None
    include_deleted: bool = False
    skip: int = Field(0, ge=0)
    limit: int = Field(20, ge=1, le=100)
