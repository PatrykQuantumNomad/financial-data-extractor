"""
Pydantic models for financial statement extraction.

Matches structure from reference code, adapted for our extraction pipeline.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class FinancialLineItem(BaseModel):
    """A single line item in a financial statement."""

    item_name: str = Field(..., description="Name of the financial line item")
    value: dict[str, float | None] = Field(
        ..., description="Dictionary mapping years/periods to values"
    )
    currency: str = Field(default="EUR", description="Currency (EUR, USD, etc)")
    unit: str = Field(default="thousands", description="Unit (thousands, millions, etc)")
    indentation_level: int = Field(
        default=0, ge=0, le=5, description="Indentation level (0=main item, 1=sub-item)"
    )
    is_subtotal: bool = Field(default=False, description="Whether this is a subtotal")
    is_total: bool = Field(default=False, description="Whether this is a total")
    confidence: Literal["high", "medium", "low"] = Field(
        default="high", description="Extraction confidence level"
    )
    footnote_refs: list[str] | None = Field(
        default=None, description="References to footnotes"
    )

    @field_validator("item_name")
    @classmethod
    def validate_item_name(cls, v: str) -> str:
        """Validate item name is not empty."""
        if not v or not v.strip():
            raise ValueError("Item name cannot be empty")
        return v.strip()


class FinancialStatement(BaseModel):
    """A financial statement with line items for multiple periods."""

    statement_type: Literal[
        "income_statement", "balance_sheet", "cash_flow_statement"
    ] = Field(..., description="Type of financial statement")
    year: int = Field(..., description="Primary fiscal year for this statement")
    period_end: str | date = Field(..., description="Period end date")
    line_items: list[FinancialLineItem] = Field(
        ..., description="List of line items in the statement"
    )
    currency: str = Field(default="EUR", description="Currency for the statement")
    unit: str = Field(default="thousands", description="Unit for values")

    @field_validator("line_items")
    @classmethod
    def validate_line_items(cls, v: list[FinancialLineItem]) -> list[FinancialLineItem]:
        """Validate line items list is not empty."""
        if not v:
            raise ValueError("Line items cannot be empty")
        return v


class ExtractionMetadata(BaseModel):
    """Metadata about the extraction process."""

    page_numbers: list[int] = Field(default_factory=list, description="Page numbers where statement was found")
    sections_found: list[str] = Field(
        default_factory=list, description="Sections identified in document"
    )
    data_quality_score: float = Field(
        ..., ge=0.0, le=1.0, description="Data quality score (0-1)"
    )
    extraction_method: str = Field(
        default="llm", description="Method used (llm, tables, hybrid)"
    )
    model_used: str = Field(..., description="LLM model used for extraction")
    tokens_used: int | None = Field(
        default=None, description="Number of tokens used"
    )
    extraction_time_seconds: float | None = Field(
        default=None, description="Time taken for extraction"
    )


class FinancialStatementExtraction(BaseModel):
    """Complete financial statement extraction with metadata."""

    statement_type: Literal[
        "income_statement", "balance_sheet", "cash_flow_statement"
    ] = Field(..., description="Type of financial statement")
    company_name: str = Field(..., description="Company name")
    fiscal_year: int = Field(..., description="Primary fiscal year")
    fiscal_year_end: date | str = Field(..., description="Fiscal year end date")
    currency: str = Field(..., description="Currency code (ISO 4217)")
    unit: str = Field(default="thousands", description="Unit (thousands, millions, etc)")
    line_items: list[FinancialLineItem] = Field(..., description="Line items")
    extraction_metadata: ExtractionMetadata = Field(..., description="Extraction metadata")

    def to_dict(self) -> dict:
        """Convert to dictionary for storage in database."""
        return self.model_dump()


class CompanyFinancials(BaseModel):
    """Complete company financial data with multiple statements."""

    company_name: str = Field(..., description="Company name")
    currency: str = Field(..., description="Primary currency")
    statements: list[FinancialStatement] = Field(
        ..., description="List of financial statements"
    )

    def to_extractions(
        self, fiscal_year: int, fiscal_year_end: date | str
    ) -> list[FinancialStatementExtraction]:
        """Convert to list of extraction objects for database storage.

        Args:
            fiscal_year: Primary fiscal year.
            fiscal_year_end: Fiscal year end date.

        Returns:
            List of FinancialStatementExtraction objects.
        """
        extractions = []
        for stmt in self.statements:
            extraction = FinancialStatementExtraction(
                statement_type=stmt.statement_type,
                company_name=self.company_name,
                fiscal_year=fiscal_year,
                fiscal_year_end=fiscal_year_end,
                currency=stmt.currency or self.currency,
                unit=stmt.unit,
                line_items=stmt.line_items,
                extraction_metadata=ExtractionMetadata(
                    data_quality_score=0.8,  # Default, should be calculated
                    model_used="unknown",
                ),
            )
            extractions.append(extraction)

        return extractions
