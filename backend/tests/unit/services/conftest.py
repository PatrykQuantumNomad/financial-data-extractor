"""
Shared fixtures for service unit tests.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.schemas.company import CompanyDomain


@pytest.fixture
def mock_company_repository() -> MagicMock:
    """Create a mock CompanyRepository for testing."""
    repository = MagicMock()
    repository.get_by_id = AsyncMock()
    repository.get_by_ticker = AsyncMock()
    repository.create = AsyncMock()
    repository.get_all = AsyncMock()
    repository.update = AsyncMock()
    repository.delete = AsyncMock()
    return repository


@pytest.fixture
def mock_document_repository() -> MagicMock:
    """Create a mock DocumentRepository for testing."""
    repository = MagicMock()
    repository.get_by_id = AsyncMock()
    repository.create = AsyncMock()
    repository.get_documents_by_company = AsyncMock()
    repository.get_documents_by_company_and_year = AsyncMock()
    repository.get_documents_by_company_and_type = AsyncMock()
    repository.update = AsyncMock()
    repository.delete = AsyncMock()
    return repository


@pytest.fixture
def mock_extraction_repository() -> MagicMock:
    """Create a mock ExtractionRepository for testing."""
    repository = MagicMock()
    repository.get_by_id = AsyncMock()
    repository.create = AsyncMock()
    repository.get_extractions_by_document = AsyncMock()
    repository.get_extraction_by_document_and_type = AsyncMock()
    repository.update = AsyncMock()
    repository.delete = AsyncMock()
    return repository


@pytest.fixture
def sample_company_data() -> CompanyDomain:
    """Sample company data for testing."""
    return CompanyDomain(
        id=1,
        name="Test Company",
        ir_url="https://example.com/investor-relations",
        primary_ticker="TEST",
        tickers=[{"exchange": "NYSE", "symbol": "TEST"}],
        created_at=datetime(2024, 1, 1),
    )


@pytest.fixture
def sample_document_data() -> dict:
    """Sample document data for testing."""
    return {
        "id": 1,
        "company_id": 1,
        "url": "https://example.com/annual-report-2023.pdf",
        "fiscal_year": 2023,
        "document_type": "Annual Report",
        "file_path": None,
        "created_at": datetime(2024, 1, 1),
    }


@pytest.fixture
def sample_extraction_data() -> dict:
    """Sample extraction data for testing."""
    return {
        "id": 1,
        "document_id": 1,
        "statement_type": "Income Statement",
        "raw_data": {"revenue": 1000000, "expenses": 800000},
        "created_at": datetime(2024, 1, 1),
    }
