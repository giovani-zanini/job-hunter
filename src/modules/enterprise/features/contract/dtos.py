"""Pydantic schemas for Contract feature."""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ContractCreateRequest(BaseModel):
    type: str = Field(..., max_length=25, description="e.g. CLT, PJ, FREELANCE")
    regional_classification: str = Field(..., max_length=4, description="e.g. BRA, USA")
    currency: str = Field("BRL", max_length=4)
    payment_periodicity: str = Field("MONTHLY", max_length=25)
    min_payment_amount: Optional[Decimal] = Field(None)
    max_payment_amount: Optional[Decimal] = Field(None)
    is_payment_disclosed: bool = Field(False)


class ContractUpdateRequest(BaseModel):
    type: Optional[str] = Field(None, max_length=25)
    regional_classification: Optional[str] = Field(None, max_length=4)
    currency: Optional[str] = Field(None, max_length=4)
    payment_periodicity: Optional[str] = Field(None, max_length=25)
    min_payment_amount: Optional[Decimal] = Field(None)
    max_payment_amount: Optional[Decimal] = Field(None)
    is_payment_disclosed: Optional[bool] = Field(None)


class ContractResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    type: str
    regional_classification: str
    currency: str
    payment_periodicity: str
    min_payment_amount: Optional[Decimal] = None
    max_payment_amount: Optional[Decimal] = None
    is_payment_disclosed: bool


class ContractDetailResponse(ContractResponse):
    deleted_at: Optional[datetime] = None


class ContractFilterParams(BaseModel):
    type: Optional[str] = Field(None)
    regional_classification: Optional[str] = Field(None)
    include_deleted: bool = Field(False)
    skip: int = Field(0, ge=0)
    limit: int = Field(20, ge=1, le=100)
