"""
Unit tests for database models.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

import pytest

from app.db.models.company import Company
from app.db.models.document import Document
from app.db.models.extraction import CompiledStatement, Extraction


@pytest.mark.unit
class TestCompanyModel:
    """Test cases for Company model."""

    def test_company_repr(self):
        """Test Company string representation."""
        # Arrange
        company = Company(
            id=1,
            name="Test Company",
            ir_url="https://example.com/ir",
            primary_ticker="TEST",
        )

        # Act
        result = str(company)

        # Assert
        assert "Company" in result
        assert "1" in result
        assert "Test Company" in result
        assert "TEST" in result

    def test_company_model_creation(self):
        """Test Company model can be instantiated."""
        # Arrange & Act
        company = Company(
            id=1,
            name="Test Company",
            ir_url="https://example.com/ir",
            primary_ticker="TEST",
            tickers=[{"exchange": "NYSE", "symbol": "TEST"}],
        )

        # Assert
        assert company.id == 1
        assert company.name == "Test Company"
        assert company.ir_url == "https://example.com/ir"
        assert company.primary_ticker == "TEST"
        assert company.tickers == [{"exchange": "NYSE", "symbol": "TEST"}]

    def test_company_model_with_nullable_fields(self):
        """Test Company model with optional fields as None."""
        # Arrange & Act
        company = Company(
            id=1,
            name="Test Company",
            ir_url="https://example.com/ir",
            primary_ticker=None,
            tickers=None,
        )

        # Assert
        assert company.primary_ticker is None
        assert company.tickers is None


@pytest.mark.unit
class TestDocumentModel:
    """Test cases for Document model."""

    def test_document_repr(self):
        """Test Document string representation."""
        # Arrange
        document = Document(
            id=1,
            company_id=1,
            url="https://example.com/annual-2023.pdf",
            fiscal_year=2023,
            document_type="Annual Report",
        )

        # Act
        result = str(document)

        # Assert
        assert "Document" in result
        assert "1" in result
        assert "2023" in result
        assert "Annual Report" in result

    def test_document_model_creation(self):
        """Test Document model can be instantiated."""
        # Arrange & Act
        document = Document(
            id=1,
            company_id=1,
            url="https://example.com/annual-2023.pdf",
            fiscal_year=2023,
            document_type="Annual Report",
            file_path="/data/pdf/annual-2023.pdf",
        )

        # Assert
        assert document.id == 1
        assert document.company_id == 1
        assert document.url == "https://example.com/annual-2023.pdf"
        assert document.fiscal_year == 2023
        assert document.document_type == "Annual Report"
        assert document.file_path == "/data/pdf/annual-2023.pdf"

    def test_document_model_with_nullable_file_path(self):
        """Test Document model with optional file_path as None."""
        # Arrange & Act
        document = Document(
            id=1,
            company_id=1,
            url="https://example.com/annual-2023.pdf",
            fiscal_year=2023,
            document_type="Annual Report",
            file_path=None,
        )

        # Assert
        assert document.file_path is None


@pytest.mark.unit
class TestExtractionModel:
    """Test cases for Extraction model."""

    def test_extraction_repr(self):
        """Test Extraction string representation."""
        # Arrange
        extraction = Extraction(
            id=1,
            document_id=1,
            statement_type="Income Statement",
            raw_data={"revenue": 1000000},
        )

        # Act
        result = str(extraction)

        # Assert
        assert "Extraction" in result
        assert "1" in result
        assert "Income Statement" in result

    def test_extraction_model_creation(self):
        """Test Extraction model can be instantiated."""
        # Arrange & Act
        extraction = Extraction(
            id=1,
            document_id=1,
            statement_type="Income Statement",
            raw_data={"revenue": 1000000, "expenses": 800000},
        )

        # Assert
        assert extraction.id == 1
        assert extraction.document_id == 1
        assert extraction.statement_type == "Income Statement"
        assert extraction.raw_data["revenue"] == 1000000
        assert extraction.raw_data["expenses"] == 800000

    def test_extraction_model_with_complex_raw_data(self):
        """Test Extraction model with complex nested raw_data."""
        # Arrange & Act
        complex_data = {
            "income_statement": {
                "revenue": 1000000,
                "operating_expenses": {
                    "r_and_d": 100000,
                    "marketing": 50000,
                },
            }
        }
        extraction = Extraction(
            id=1,
            document_id=1,
            statement_type="Income Statement",
            raw_data=complex_data,
        )

        # Assert
        assert extraction.raw_data["income_statement"]["revenue"] == 1000000
        assert extraction.raw_data["income_statement"]["operating_expenses"]["r_and_d"] == 100000


@pytest.mark.unit
class TestCompiledStatementModel:
    """Test cases for CompiledStatement model."""

    def test_compiled_statement_repr(self):
        """Test CompiledStatement string representation."""
        # Arrange
        compiled = CompiledStatement(
            id=1,
            company_id=1,
            statement_type="Income Statement",
            data={"2023": {"revenue": 1000000}},
        )

        # Act
        result = str(compiled)

        # Assert
        assert "CompiledStatement" in result
        assert "1" in result
        assert "Income Statement" in result

    def test_compiled_statement_model_creation(self):
        """Test CompiledStatement model can be instantiated."""
        # Arrange & Act
        compiled = CompiledStatement(
            id=1,
            company_id=1,
            statement_type="Income Statement",
            data={"2023": {"revenue": 1000000}},
        )

        # Assert
        assert compiled.id == 1
        assert compiled.company_id == 1
        assert compiled.statement_type == "Income Statement"
        assert compiled.data["2023"]["revenue"] == 1000000

    def test_compiled_statement_model_with_multi_year_data(self):
        """Test CompiledStatement model with multi-year data."""
        # Arrange & Act
        multi_year_data = {
            "2021": {"revenue": 800000},
            "2022": {"revenue": 900000},
            "2023": {"revenue": 1000000},
        }
        compiled = CompiledStatement(
            id=1,
            company_id=1,
            statement_type="Income Statement",
            data=multi_year_data,
        )

        # Assert
        assert compiled.data["2021"]["revenue"] == 800000
        assert compiled.data["2022"]["revenue"] == 900000
        assert compiled.data["2023"]["revenue"] == 1000000
