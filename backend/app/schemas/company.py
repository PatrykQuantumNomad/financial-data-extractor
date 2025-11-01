"""
Pydantic schemas for Company model.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CompanyBase(BaseModel):
    """Base schema for Company with common fields."""

    name: str = Field(..., description="Company name", min_length=1, max_length=255)
    ir_url: str = Field(..., description="Investor relations URL")
    primary_ticker: str | None = Field(
        None, description="Primary stock ticker symbol", max_length=10
    )
    tickers: list[dict[str, str]] | None = Field(
        None, description="List of ticker symbols and exchanges"
    )


class CompanyCreate(CompanyBase):
    """Schema for creating a new company."""

    pass


class CompanyUpdate(BaseModel):
    """Schema for updating a company."""

    name: str | None = Field(None, description="Company name", min_length=1, max_length=255)
    ir_url: str | None = Field(None, description="Investor relations URL")
    primary_ticker: str | None = Field(
        None, description="Primary stock ticker symbol", max_length=10
    )
    tickers: list[dict[str, str]] | None = Field(
        None, description="List of ticker symbols and exchanges"
    )


class CompanyResponse(CompanyBase):
    """Schema for company response."""

    id: int = Field(..., description="Company ID")
    created_at: datetime | None = Field(None, description="Creation timestamp")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
