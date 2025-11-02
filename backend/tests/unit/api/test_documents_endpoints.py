"""
Unit tests for Documents API endpoints.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

import pytest
from fastapi import status
from fastapi.testclient import TestClient


@pytest.mark.unit
class TestDocumentsEndpoints:
    """Test cases for Documents endpoints."""

    def test_create_document_success(
        self, test_client: TestClient, mock_document_service, sample_document_data
    ):
        """Test successful document creation."""
        # Arrange
        mock_document_service.create_document.return_value = sample_document_data
        document_data = {
            "company_id": 1,
            "url": "https://example.com/annual-report-2023.pdf",
            "fiscal_year": 2023,
            "document_type": "Annual Report",
        }

        # Act
        response = test_client.post("/documents", json=document_data)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["company_id"] == 1
        assert data["fiscal_year"] == 2023
        mock_document_service.create_document.assert_called_once()

    def test_create_document_with_invalid_fiscal_year(
        self, test_client: TestClient, mock_document_service
    ):
        """Test document creation with invalid fiscal year."""
        # Arrange
        invalid_data = {
            "company_id": 1,
            "url": "https://example.com/annual-report-2023.pdf",
            "fiscal_year": 1800,  # Below minimum
            "document_type": "Annual Report",
        }

        # Act
        response = test_client.post("/documents", json=invalid_data)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_document_by_id_success(
        self, test_client: TestClient, mock_document_service, sample_document_data
    ):
        """Test successful retrieval of document by ID."""
        # Arrange
        mock_document_service.get_document.return_value = sample_document_data

        # Act
        response = test_client.get("/documents/1")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == 1
        mock_document_service.get_document.assert_called_once_with(1)

    def test_get_document_by_id_not_found(
        self, test_client: TestClient, mock_document_service
    ):
        """Test retrieval of non-existent document."""
        # Arrange
        from app.core.exceptions.custom_exceptions import JSONFileNotFoundError
        mock_document_service.get_document.side_effect = JSONFileNotFoundError(
            filename="document_999.json"
        )

        # Act
        response = test_client.get("/documents/999")

        # Assert
        mock_document_service.get_document.assert_called_once_with(999)

    def test_list_documents_by_company_success(
        self, test_client: TestClient, mock_document_service, sample_document_data
    ):
        """Test successful listing of documents by company."""
        # Arrange
        mock_document_service.get_documents_by_company.return_value = [sample_document_data]

        # Act
        response = test_client.get("/documents/companies/1?skip=0&limit=10")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        mock_document_service.get_documents_by_company.assert_called_once_with(
            company_id=1, skip=0, limit=10
        )

    def test_list_documents_by_company_with_default_pagination(
        self, test_client: TestClient, mock_document_service, sample_document_data
    ):
        """Test listing documents by company with default pagination."""
        # Arrange
        mock_document_service.get_documents_by_company.return_value = [sample_document_data]

        # Act
        response = test_client.get("/documents/companies/1")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        mock_document_service.get_documents_by_company.assert_called_once_with(
            company_id=1, skip=0, limit=100
        )

    def test_get_documents_by_company_and_year_success(
        self, test_client: TestClient, mock_document_service, sample_document_data
    ):
        """Test successful retrieval of documents by company and year."""
        # Arrange
        mock_document_service.get_documents_by_company_and_year.return_value = [
            sample_document_data
        ]

        # Act
        response = test_client.get("/documents/companies/1/fiscal-year/2023")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        mock_document_service.get_documents_by_company_and_year.assert_called_once_with(
            company_id=1, fiscal_year=2023
        )

    def test_get_documents_by_company_and_year_with_invalid_year(
        self, test_client: TestClient
    ):
        """Test retrieval with invalid fiscal year."""
        # Arrange - year outside valid range
        # Act
        response = test_client.get("/documents/companies/1/fiscal-year/1800")

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_documents_by_company_and_type_success(
        self, test_client: TestClient, mock_document_service, sample_document_data
    ):
        """Test successful retrieval of documents by company and type."""
        # Arrange
        mock_document_service.get_documents_by_company_and_type.return_value = [
            sample_document_data
        ]

        # Act
        response = test_client.get(
            "/documents/companies/1/type/Annual%20Report?skip=0&limit=10"
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        mock_document_service.get_documents_by_company_and_type.assert_called_once_with(
            company_id=1, document_type="Annual Report", skip=0, limit=10
        )

    def test_get_documents_by_company_and_type_with_invalid_pagination(
        self, test_client: TestClient
    ):
        """Test retrieval with invalid pagination."""
        # Arrange - negative skip
        # Act
        response = test_client.get(
            "/documents/companies/1/type/Annual%20Report?skip=-1&limit=10"
        )

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_update_document_success(
        self, test_client: TestClient, mock_document_service, sample_document_data
    ):
        """Test successful document update."""
        # Arrange
        updated_data = sample_document_data.copy()
        updated_data["fiscal_year"] = 2024
        mock_document_service.update_document.return_value = updated_data
        update_data = {"fiscal_year": 2024}

        # Act
        response = test_client.put("/documents/1", json=update_data)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["fiscal_year"] == 2024
        mock_document_service.update_document.assert_called_once()

    def test_update_document_with_invalid_data(self, test_client: TestClient):
        """Test document update with invalid data."""
        # Arrange
        invalid_data = {"fiscal_year": 2101}  # Above maximum

        # Act
        response = test_client.put("/documents/1", json=invalid_data)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_delete_document_success(
        self, test_client: TestClient, mock_document_service
    ):
        """Test successful document deletion."""
        # Arrange
        mock_document_service.delete_document.return_value = None

        # Act
        response = test_client.delete("/documents/1")

        # Assert
        assert response.status_code == status.HTTP_204_NO_CONTENT
        mock_document_service.delete_document.assert_called_once_with(1)

    def test_delete_document_not_found(
        self, test_client: TestClient, mock_document_service
    ):
        """Test deletion of non-existent document."""
        # Arrange
        from app.core.exceptions.custom_exceptions import JSONFileNotFoundError
        mock_document_service.delete_document.side_effect = JSONFileNotFoundError(
            filename="document_999.json"
        )

        # Act
        response = test_client.delete("/documents/999")

        # Assert
        mock_document_service.delete_document.assert_called_once_with(999)

    def test_create_document_with_file_path(
        self, test_client: TestClient, mock_document_service, sample_document_data
    ):
        """Test document creation with file path."""
        # Arrange
        sample_document_data["file_path"] = "/data/pdfs/annual-report-2023.pdf"
        mock_document_service.create_document.return_value = sample_document_data
        document_data = {
            "company_id": 1,
            "url": "https://example.com/annual-report-2023.pdf",
            "fiscal_year": 2023,
            "document_type": "Annual Report",
            "file_path": "/data/pdfs/annual-report-2023.pdf",
        }

        # Act
        response = test_client.post("/documents", json=document_data)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["file_path"] == "/data/pdfs/annual-report-2023.pdf"

    def test_list_documents_by_company_with_limit_over_maximum(
        self, test_client: TestClient
    ):
        """Test listing documents with limit exceeding maximum."""
        # Arrange - limit > 100
        # Act
        response = test_client.get("/documents/companies/1?skip=0&limit=150")

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_list_documents_empty_result(
        self, test_client: TestClient, mock_document_service
    ):
        """Test listing documents with empty result."""
        # Arrange
        mock_document_service.get_documents_by_company.return_value = []

        # Act
        response = test_client.get("/documents/companies/1")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data == []
