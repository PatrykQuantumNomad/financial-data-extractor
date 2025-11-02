"""
Shared fixtures for API unit tests.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from app.api.v1.endpoints import (
    companies_router,
    compiled_statements_router,
    documents_router,
    extractions_router,
    tasks_router,
)
from app.schemas.company import CompanyDomain


@pytest.fixture
def mock_company_service() -> MagicMock:
    """Create a mock CompanyService for testing."""
    service = AsyncMock()
    service.create_company = AsyncMock()
    service.get_all_companies = AsyncMock()
    service.get_company = AsyncMock()
    service.get_company_by_ticker = AsyncMock()
    service.update_company = AsyncMock()
    service.delete_company = AsyncMock()
    return service


@pytest.fixture
def mock_document_service() -> MagicMock:
    """Create a mock DocumentService for testing."""
    service = AsyncMock()
    service.create_document = AsyncMock()
    service.get_document = AsyncMock()
    service.get_documents_by_company = AsyncMock()
    service.get_documents_by_company_and_year = AsyncMock()
    service.get_documents_by_company_and_type = AsyncMock()
    service.update_document = AsyncMock()
    service.delete_document = AsyncMock()
    return service


@pytest.fixture
def mock_extraction_service() -> MagicMock:
    """Create a mock ExtractionService for testing."""
    service = AsyncMock()
    service.create_extraction = AsyncMock()
    service.get_extraction = AsyncMock()
    service.get_extractions_by_document = AsyncMock()
    service.get_extraction_by_document_and_type = AsyncMock()
    service.update_extraction = AsyncMock()
    service.delete_extraction = AsyncMock()
    return service


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


@pytest.fixture
def test_app(mock_company_service, mock_document_service, mock_extraction_service) -> FastAPI:
    """
    Create a FastAPI test app with mocked dependencies.

    Args:
        mock_company_service: Mock CompanyService.
        mock_document_service: Mock DocumentService.
        mock_extraction_service: Mock ExtractionService.

    Returns:
        FastAPI test application.
    """
    app = FastAPI()
    app.include_router(companies_router)
    app.include_router(documents_router)
    app.include_router(extractions_router)
    app.include_router(compiled_statements_router)
    app.include_router(tasks_router)

    # Override dependencies with mocks
    from app.services import dependencies

    async def override_company_service():
        return mock_company_service

    async def override_document_service():
        return mock_document_service

    async def override_extraction_service():
        return mock_extraction_service

    app.dependency_overrides[dependencies.get_company_service] = override_company_service
    app.dependency_overrides[dependencies.get_document_service] = override_document_service
    app.dependency_overrides[dependencies.get_extraction_service] = override_extraction_service

    return app


@pytest.fixture
def test_client(test_app: FastAPI) -> TestClient:
    """
    Create a TestClient for the test app.

    Args:
        test_app: FastAPI test application.

    Returns:
        TestClient instance.
    """
    return TestClient(test_app)


@pytest.fixture
def mock_request() -> Request:
    """
    Create a mock Request object for testing middleware.

    Returns:
        Mock Request.
    """
    request = MagicMock(spec=Request)
    request.state = MagicMock()
    request.url.path = "/test/path"
    request.method = "GET"
    return request


@pytest.fixture
def mock_call_next() -> MagicMock:
    """
    Create a mock call_next function for testing middleware.

    Returns:
        Mock call_next coroutine.
    """

    async def call_next(request):
        response = MagicMock()
        response.headers = {}
        return response

    return AsyncMock(side_effect=call_next)
