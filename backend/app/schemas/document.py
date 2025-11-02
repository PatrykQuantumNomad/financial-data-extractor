"""
Pydantic schemas for Document model.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DocumentBase(BaseModel):
    """Base schema for Document with common fields."""

    company_id: int = Field(..., description="ID of the company this document belongs to")
    url: str = Field(..., description="URL where the document was found")
    fiscal_year: int = Field(..., description="Fiscal year of the document", ge=1900, le=2100)
    document_type: str = Field(..., description="Type of document", max_length=50, min_length=1)
    file_path: str | None = Field(None, description="Local file path if downloaded")


class DocumentCreate(DocumentBase):
    """Schema for creating a new document."""

    pass


class DocumentUpdate(BaseModel):
    """Schema for updating a document."""

    url: str | None = Field(None, description="URL where the document was found")
    fiscal_year: int | None = Field(
        None, description="Fiscal year of the document", ge=1900, le=2100
    )
    document_type: str | None = Field(
        None, description="Type of document", max_length=50, min_length=1
    )
    file_path: str | None = Field(None, description="Local file path if downloaded")


class DocumentResponse(DocumentBase):
    """Schema for document response."""

    id: int = Field(..., description="Document ID")
    created_at: datetime | None = Field(None, description="Creation timestamp")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
