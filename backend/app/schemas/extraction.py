"""
Pydantic schemas for Extraction and CompiledStatement models.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# Extraction schemas
class ExtractionBase(BaseModel):
    """Base schema for Extraction with common fields."""

    document_id: int = Field(..., description="ID of the document this extraction belongs to")
    statement_type: str = Field(
        ..., description="Type of financial statement", max_length=50, min_length=1
    )
    raw_data: dict[str, Any] = Field(..., description="Raw extracted data as dictionary")


class ExtractionCreate(ExtractionBase):
    """Schema for creating a new extraction."""

    pass


class ExtractionUpdate(BaseModel):
    """Schema for updating an extraction."""

    raw_data: dict[str, Any] | None = Field(
        None, description="Raw extracted data as dictionary"
    )


class ExtractionResponse(ExtractionBase):
    """Schema for extraction response."""

    id: int = Field(..., description="Extraction ID")
    created_at: datetime | None = Field(None, description="Creation timestamp")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# CompiledStatement schemas
class CompiledStatementBase(BaseModel):
    """Base schema for CompiledStatement with common fields."""

    company_id: int = Field(
        ..., description="ID of the company this compiled statement belongs to"
    )
    statement_type: str = Field(
        ..., description="Type of financial statement", max_length=50, min_length=1
    )
    data: dict[str, Any] = Field(..., description="Compiled financial data as dictionary")


class CompiledStatementCreate(CompiledStatementBase):
    """Schema for creating a new compiled statement."""

    pass


class CompiledStatementUpdate(BaseModel):
    """Schema for updating a compiled statement."""

    data: dict[str, Any] | None = Field(
        None, description="Compiled financial data as dictionary"
    )


class CompiledStatementResponse(CompiledStatementBase):
    """Schema for compiled statement response."""

    id: int = Field(..., description="Compiled statement ID")
    updated_at: datetime | None = Field(None, description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
