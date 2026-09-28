"""Pydantic schemas for Company feature."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


# --- Request Schemas ---

class CompanyCreateRequest(BaseModel):
    """Schema for creating a new company."""
    
    name: str = Field(..., max_length=150, description="Company name")
    website: str = Field(..., max_length=255, description="Company website URL")


class CompanyUpdateRequest(BaseModel):
    """Schema for updating a company."""
    
    name: Optional[str] = Field(None, max_length=150, description="Company name")
    website: Optional[str] = Field(None, max_length=255, description="Company website URL")


# --- Response Schemas ---

class CompanyResponse(BaseModel):
    """Schema for company response."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    website: str


class CompanyDetailResponse(BaseModel):
    """Schema for detailed company response."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    website: str
    deleted_at: Optional[datetime] = None


# --- Filter Schemas ---

class CompanyFilterParams(BaseModel):
    """Schema for company list filters."""
    
    name: Optional[str] = Field(None, description="Filter by name (partial match)")
    include_deleted: bool = Field(False, description="Include soft deleted companies")
    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(20, ge=1, le=100, description="Maximum number of records to return")
