"""Pydantic schemas for Certificate feature."""

from datetime import date, datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field


# --- Request Schemas ---


class CertificateCreateRequest(BaseModel):
    """Schema for creating a new certificate."""

    name: str = Field(..., max_length=100, description="Certificate name")
    issuer: str = Field(..., max_length=100, description="Issuing organization")
    issue_date: date = Field(..., description="Issue date")
    expiration_date: Optional[date] = Field(
        None, description="Expiration date (optional)"
    )
    credential_url: Optional[str] = Field(
        None, max_length=255, description="Credential URL"
    )
    skill_ids: List[int] = Field(default=[], description="Skill IDs to associate")


class CertificateUpdateRequest(BaseModel):
    """Schema for updating a certificate."""

    name: Optional[str] = Field(None, max_length=100, description="Certificate name")
    issuer: Optional[str] = Field(
        None, max_length=100, description="Issuing organization"
    )
    issue_date: Optional[date] = Field(None, description="Issue date")
    expiration_date: Optional[date] = Field(None, description="Expiration date")
    credential_url: Optional[str] = Field(
        None, max_length=255, description="Credential URL"
    )


# --- Response Schemas ---


class CertificateResponse(BaseModel):
    """Schema for certificate response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    name: str
    issuer: str
    issue_date: date
    expiration_date: Optional[date] = None
    credential_url: Optional[str] = None


class CertificateDetailResponse(BaseModel):
    """Schema for detailed certificate response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    name: str
    issuer: str
    issue_date: date
    expiration_date: Optional[date] = None
    credential_url: Optional[str] = None
    deleted_at: Optional[datetime] = None


# --- Filter Schemas ---


class CertificateFilterParams(BaseModel):
    """Schema for certificate list filters."""

    user_id: Optional[int] = Field(None, description="Filter by user ID")
    name: Optional[str] = Field(None, description="Filter by name (partial match)")
    issuer: Optional[str] = Field(None, description="Filter by issuer (partial match)")
    include_deleted: bool = Field(
        False, description="Include soft deleted certificates"
    )
    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(
        20, ge=1, le=100, description="Maximum number of records to return"
    )
