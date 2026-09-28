"""Pydantic schemas for Vacancy feature."""

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


# --- VacancyRequirement DTOs ---

class VacancyRequirementCreateRequest(BaseModel):
    requirement_id: int
    optional_requirement_id: Optional[int] = None
    level: int = Field(..., ge=0)
    experience_years: Optional[int] = Field(None, ge=0)
    requirement_type: str = Field(..., max_length=25)


class VacancyRequirementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    vacancy_id: int
    requirement_id: int
    optional_requirement_id: Optional[int] = None
    level: int
    experience_years: Optional[int] = None
    requirement_type: str


# --- VacancyResponsability DTOs ---

class VacancyResponsabilityCreateRequest(BaseModel):
    responsability_id: int


class VacancyResponsabilityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    vacancy_id: int
    responsability_id: int


# --- Vacancy DTOs ---

class VacancyCreateRequest(BaseModel):
    title: str = Field(..., max_length=100)
    description: str
    company_unit_id: int
    contract_id: Optional[int] = None
    seniority_level: str = Field(..., max_length=25)
    published_date: date
    custom_data: Optional[Dict[str, Any]] = None


class VacancyUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    company_unit_id: Optional[int] = None
    contract_id: Optional[int] = None
    seniority_level: Optional[str] = Field(None, max_length=25)
    published_date: Optional[date] = None
    custom_data: Optional[Dict[str, Any]] = None


class VacancyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    company_unit_id: int
    contract_id: Optional[int] = None
    seniority_level: str
    published_date: date
    custom_data: Optional[Dict[str, Any]] = None


class VacancyDetailResponse(VacancyResponse):
    deleted_at: Optional[datetime] = None
    vacancy_requirements: List[VacancyRequirementResponse] = []
    vacancy_responsabilities: List[VacancyResponsabilityResponse] = []


class VacancyFilterParams(BaseModel):
    title: Optional[str] = None
    seniority_level: Optional[str] = None
    company_unit_id: Optional[int] = None
    include_deleted: bool = False
    skip: int = Field(0, ge=0)
    limit: int = Field(20, ge=1, le=100)
