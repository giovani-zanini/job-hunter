"""Pydantic schemas for Link feature.

This module provides data transfer objects (DTOs) for the Link feature,
organized into four main categories:

    - Enum Definitions: Link type classifications for categorizing links.
    - Request Schemas: For API request payloads (create, update operations).
    - Response Schemas: For API response payloads (link data, detail view).
    - Filter Schemas: For query filtering and pagination parameters.

All schemas use Pydantic's BaseModel for validation and serialization.
Some schemas include model_config with from_attributes=True for ORM compatibility.
Field aliases are used to handle the reserved Python keyword 'from'.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# --- Enum Definitions ---


class LinkType(str, Enum):
    """Enumeration of supported link types.

    Used to categorize links by their purpose and format.

    Attributes:
        SOCIAL_MEDIA: Links to social media profiles (LinkedIn, Instagram, etc.).
        EMAIL: Email addresses for professional contact.
        CELLPHONE: Phone numbers for direct communication.
    """

    SOCIAL_MEDIA = "SOCIAL_MEDIA"
    EMAIL = "EMAIL"
    CELLPHONE = "CELLPHONE"


# --- Request Schemas ---


class LinkCreateRequest(BaseModel):
    """Schema for creating a new link.

    Used in POST requests to create a new link for a user. All fields are
    required. Links can represent social media profiles, email addresses,
    or phone numbers.

    Attributes:
        user_id (int): The ID of the user who owns this link.
        type (LinkType): Type of link (SOCIAL_MEDIA, EMAIL, or CELLPHONE).
        from_ (str): Origin platform or service (gmail, linkedin, etc.),
            maximum 50 characters. Uses alias 'from' in JSON.
        value (str): The actual link value (URL, email address, phone number),
            maximum 150 characters.
    """

    type: LinkType = Field(
        ..., description="Type of link (SOCIAL_MEDIA, EMAIL, CELLPHONE)"
    )
    from_: str = Field(
        ..., max_length=50, alias="from", description="Origin (gmail, linkedin, etc.)"
    )
    value: str = Field(
        ..., max_length=150, description="Link value (URL, email, phone number)"
    )

    model_config = ConfigDict(populate_by_name=True)


class LinkUpdateRequest(BaseModel):
    """Schema for updating a link.

    Used in PATCH/PUT requests to update an existing link. All fields are
    optional, allowing partial updates. Only provided fields will be modified.

    Attributes:
        type (Optional[LinkType]): New type classification for the link.
        from_ (Optional[str]): Updated origin platform or service,
            maximum 50 characters. Uses alias 'from' in JSON.
        value (Optional[str]): Updated link value (URL, email, phone number),
            maximum 150 characters.
    """

    type: Optional[LinkType] = Field(None, description="Type of link")
    from_: Optional[str] = Field(
        None, max_length=50, alias="from", description="Origin"
    )
    value: Optional[str] = Field(None, max_length=150, description="Link value")

    model_config = ConfigDict(populate_by_name=True)


# --- Response Schemas ---


class LinkResponse(BaseModel):
    """Schema for link response.

    Represents a basic link response containing core link information.
    Used in list endpoints and basic link retrieval responses.

    Attributes:
        id (int): The unique identifier of the link.
        user_id (int): The ID of the user who owns this link.
        type (str): Type classification of the link.
        from_ (str): Origin platform or service. Uses alias 'from' in JSON.
        value (str): The actual link value (URL, email, phone number).
    """

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    user_id: int
    type: str
    from_: str = Field(alias="from")
    value: str


class LinkDetailResponse(BaseModel):
    """Schema for detailed link response.

    Represents a comprehensive link response with extended information
    including soft-deletion status. Used in link detail endpoints
    (GET /links/{id}).

    Attributes:
        id (int): The unique identifier of the link.
        user_id (int): The ID of the user who owns this link.
        type (str): Type classification of the link.
        from_ (str): Origin platform or service. Uses alias 'from' in JSON.
        value (str): The actual link value (URL, email, phone number).
        deleted_at (Optional[datetime]): Timestamp when the link was soft-deleted,
            or None if the link is active.
    """

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    user_id: int
    type: str
    from_: str = Field(alias="from")
    value: str
    deleted_at: Optional[datetime] = None


# --- Filter Schemas ---


class LinkFilterParams(BaseModel):
    """Schema for link list filters.

    Used in GET requests to filter and paginate link results. Supports partial
    text matching for the from_ field. Implements cursor-based pagination
    with skip/limit parameters.

    Attributes:
        user_id (Optional[int]): Filter links by user ID. If provided, only
            links belonging to this user are returned.
        type (Optional[LinkType]): Filter links by type classification.
        from_ (Optional[str]): Filter links by origin using partial string matching
            (case-insensitive). Uses alias 'from' in JSON.
        include_deleted (bool): Include soft-deleted links in results. Defaults
            to False, only active links are returned by default.
        skip (int): Number of records to skip from the beginning of the result set.
            Used for pagination. Must be non-negative. Defaults to 0.
        limit (int): Maximum number of records to return in a single response.
            Must be between 1 and 100 inclusive. Defaults to 20.
    """

    user_id: Optional[int] = Field(None, description="Filter by user ID")
    type: Optional[LinkType] = Field(None, description="Filter by link type")
    from_: Optional[str] = Field(
        None, alias="from", description="Filter by origin (partial match)"
    )
    include_deleted: bool = Field(False, description="Include soft deleted links")
    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(
        20, ge=1, le=100, description="Maximum number of records to return"
    )

    model_config = ConfigDict(populate_by_name=True)
