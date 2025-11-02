"""
Pydantic schemas for Company model.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

from datetime import datetime

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


class CompanyDomain(CompanyBase):
    """Domain schema for Company used in repository/service layer.

    This schema represents the complete company entity with all database fields.
    Used internally between repository and service layers for type safety.
    """

    id: int = Field(..., description="Company ID")
    created_at: datetime | None = Field(None, description="Creation timestamp")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class CompanyResponse(CompanyDomain):
    """Schema for company API response.

    Currently identical to CompanyDomain, but kept separate for future
    API-specific extensions (e.g., computed fields, links, etc.).
    """

    pass
