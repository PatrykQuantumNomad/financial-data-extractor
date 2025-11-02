"""
Unit tests for Pydantic schemas.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""
from datetime import datetime

import pytest

from app.schemas.company import CompanyBase, CompanyCreate, CompanyResponse, CompanyUpdate
from app.schemas.document import DocumentBase, DocumentCreate, DocumentResponse, DocumentUpdate
from app.schemas.extraction import (
    CompiledStatementBase,
    CompiledStatementResponse,
    CompiledStatementUpdate,
    ExtractionBase,
    ExtractionCreate,
    ExtractionResponse,
    ExtractionUpdate,
)


@pytest.mark.unit
class TestCompanySchemas:
    """Test cases for Company schemas."""

    def test_company_base_creation(self):
        """Test CompanyBase schema can be instantiated."""
        # Arrange & Act
        company = CompanyBase(
            name="Test Company",
            ir_url="https://example.com/ir",
            primary_ticker="TEST",
            tickers=[{"exchange": "NYSE", "symbol": "TEST"}],
        )

        # Assert
        assert company.name == "Test Company"
        assert company.ir_url == "https://example.com/ir"
        assert company.primary_ticker == "TEST"
        assert company.tickers == [{"exchange": "NYSE", "symbol": "TEST"}]

    def test_company_create_validation(self):
        """Test CompanyCreate schema validation."""
        # Arrange & Act
        company = CompanyCreate(
            name="Test Company",
            ir_url="https://example.com/ir",
            primary_ticker="TEST",
        )

        # Assert
        assert company.name == "Test Company"
        assert isinstance(company, CompanyBase)

    def test_company_create_with_invalid_name_length(self):
        """Test CompanyCreate fails with invalid name length."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError):  # Pydantic validation error
            CompanyCreate(name="", ir_url="https://example.com/ir")  # Empty name

    def test_company_response_with_all_fields(self):
        """Test CompanyResponse schema includes all fields."""
        # Arrange & Act
        company = CompanyResponse(
            id=1,
            name="Test Company",
            ir_url="https://example.com/ir",
            primary_ticker="TEST",
            tickers=[{"exchange": "NYSE", "symbol": "TEST"}],
            created_at=datetime(2024, 1, 1),
        )

        # Assert
        assert company.id == 1
        assert company.name == "Test Company"
        assert company.created_at == datetime(2024, 1, 1)

    def test_company_update_all_fields_optional(self):
        """Test CompanyUpdate schema with all optional fields."""
        # Arrange & Act
        company = CompanyUpdate()
        # All fields should be None
        assert company.name is None
        assert company.ir_url is None
        assert company.primary_ticker is None
        assert company.tickers is None

    def test_company_update_with_partial_data(self):
        """Test CompanyUpdate schema with partial data."""
        # Arrange & Act
        company = CompanyUpdate(name="Updated Name")
        assert company.name == "Updated Name"


@pytest.mark.unit
class TestDocumentSchemas:
    """Test cases for Document schemas."""

    def test_document_base_creation(self):
        """Test DocumentBase schema can be instantiated."""
        # Arrange & Act
        document = DocumentBase(
            company_id=1,
            url="https://example.com/annual-2023.pdf",
            fiscal_year=2023,
            document_type="Annual Report",
            file_path=None,
        )

        # Assert
        assert document.company_id == 1
        assert document.url == "https://example.com/annual-2023.pdf"
        assert document.fiscal_year == 2023
        assert document.document_type == "Annual Report"

    def test_document_create_validation(self):
        """Test DocumentCreate schema validation."""
        # Arrange & Act
        document = DocumentCreate(
            company_id=1,
            url="https://example.com/annual-2023.pdf",
            fiscal_year=2023,
            document_type="Annual Report",
        )

        # Assert
        assert isinstance(document, DocumentBase)

    def test_document_create_with_invalid_fiscal_year(self):
        """Test DocumentCreate fails with invalid fiscal year."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError):  # Pydantic validation error
            DocumentCreate(
                company_id=1,
                url="https://example.com/annual-2023.pdf",
                fiscal_year=1800,  # Below minimum
                document_type="Annual Report",
            )

    def test_document_response_with_all_fields(self):
        """Test DocumentResponse schema includes all fields."""
        # Arrange & Act
        document = DocumentResponse(
            id=1,
            company_id=1,
            url="https://example.com/annual-2023.pdf",
            fiscal_year=2023,
            document_type="Annual Report",
            file_path="/data/annual-2023.pdf",
            created_at=datetime(2024, 1, 1),
        )

        # Assert
        assert document.id == 1
        assert document.created_at == datetime(2024, 1, 1)

    def test_document_update_with_partial_data(self):
        """Test DocumentUpdate schema with partial data."""
        # Arrange & Act
        document = DocumentUpdate(fiscal_year=2024)
        assert document.fiscal_year == 2024


@pytest.mark.unit
class TestExtractionSchemas:
    """Test cases for Extraction schemas."""

    def test_extraction_base_creation(self):
        """Test ExtractionBase schema can be instantiated."""
        # Arrange & Act
        extraction = ExtractionBase(
            document_id=1,
            statement_type="Income Statement",
            raw_data={"revenue": 1000000},
        )

        # Assert
        assert extraction.document_id == 1
        assert extraction.statement_type == "Income Statement"
        assert extraction.raw_data["revenue"] == 1000000

    def test_extraction_create_validation(self):
        """Test ExtractionCreate schema validation."""
        # Arrange & Act
        extraction = ExtractionCreate(
            document_id=1,
            statement_type="Income Statement",
            raw_data={"revenue": 1000000},
        )

        # Assert
        assert isinstance(extraction, ExtractionBase)

    def test_extraction_response_with_all_fields(self):
        """Test ExtractionResponse schema includes all fields."""
        # Arrange & Act
        extraction = ExtractionResponse(
            id=1,
            document_id=1,
            statement_type="Income Statement",
            raw_data={"revenue": 1000000},
            created_at=datetime(2024, 1, 1),
        )

        # Assert
        assert extraction.id == 1
        assert extraction.created_at == datetime(2024, 1, 1)

    def test_extraction_update_with_complex_raw_data(self):
        """Test ExtractionUpdate schema with complex raw_data."""
        # Arrange & Act
        complex_data = {
            "income_statement": {
                "revenue": 1000000,
                "operating_expenses": {"r_and_d": 100000},
            }
        }
        extraction = ExtractionUpdate(raw_data=complex_data)

        # Assert
        assert extraction.raw_data["income_statement"]["revenue"] == 1000000


@pytest.mark.unit
class TestCompiledStatementSchemas:
    """Test cases for CompiledStatement schemas."""

    def test_compiled_statement_base_creation(self):
        """Test CompiledStatementBase schema can be instantiated."""
        # Arrange & Act
        compiled = CompiledStatementBase(
            company_id=1,
            statement_type="Income Statement",
            data={"2023": {"revenue": 1000000}},
        )

        # Assert
        assert compiled.company_id == 1
        assert compiled.statement_type == "Income Statement"
        assert compiled.data["2023"]["revenue"] == 1000000

    def test_compiled_statement_response_with_all_fields(self):
        """Test CompiledStatementResponse schema includes all fields."""
        # Arrange & Act
        compiled = CompiledStatementResponse(
            id=1,
            company_id=1,
            statement_type="Income Statement",
            data={"2023": {"revenue": 1000000}},
            updated_at=datetime(2024, 1, 1),
        )

        # Assert
        assert compiled.id == 1
        assert compiled.updated_at == datetime(2024, 1, 1)

    def test_compiled_statement_update_with_multi_year_data(self):
        """Test CompiledStatementUpdate schema with multi-year data."""
        # Arrange & Act
        multi_year_data = {
            "2021": {"revenue": 800000},
            "2022": {"revenue": 900000},
            "2023": {"revenue": 1000000},
        }
        compiled = CompiledStatementUpdate(data=multi_year_data)

        # Assert
        assert compiled.data["2021"]["revenue"] == 800000
        assert compiled.data["2023"]["revenue"] == 1000000
