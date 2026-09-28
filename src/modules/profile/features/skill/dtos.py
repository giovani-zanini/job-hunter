"""Pydantic schemas for Skill feature."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class SkillCategory(str, Enum):
    """Enum for skill categories."""
    
    LANGUAGE = "LANGUAGE"
    TOOL = "TOOL"
    FRAMEWORK = "FRAMEWORK"


# --- Request Schemas ---

class SkillCreateRequest(BaseModel):
    """Schema for creating a new skill."""
    
    name: str = Field(..., max_length=100, description="Skill name")
    category: SkillCategory = Field(..., description="Skill category")


class SkillUpdateRequest(BaseModel):
    """Schema for updating a skill."""
    
    name: Optional[str] = Field(None, max_length=100, description="Skill name")
    category: Optional[SkillCategory] = Field(None, description="Skill category")


# --- Response Schemas ---

class SkillResponse(BaseModel):
    """Schema for skill response."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    category: SkillCategory


class SkillDetailResponse(BaseModel):
    """Schema for detailed skill response."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    category: SkillCategory
    deleted_at: Optional[datetime] = None


# --- Filter Schemas ---

class SkillFilterParams(BaseModel):
    """Schema for skill list filters."""
    
    name: Optional[str] = Field(None, description="Filter by name (partial match)")
    category: Optional[SkillCategory] = Field(None, description="Filter by category")
    include_deleted: bool = Field(False, description="Include soft deleted skills")
    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(20, ge=1, le=100, description="Maximum number of records to return")
