"""
Unit tests for Companies API endpoints.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

import pytest
from fastapi import status
from fastapi.testclient import TestClient


@pytest.mark.unit
class TestCompaniesEndpoints:
    """Test cases for Companies endpoints."""

    def test_create_company_success(
        self,
        test_client: TestClient,
        mock_company_service,
        sample_company_data,
    ):
        """Test successful company creation."""
        # Arrange
        mock_company_service.create_company.return_value = sample_company_data
        company_data = {
            "name": "Test Company",
            "ir_url": "https://example.com/investor-relations",
            "primary_ticker": "TEST",
        }

        # Act
        response = test_client.post("/companies", json=company_data)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "Test Company"
        assert data["primary_ticker"] == "TEST"
        mock_company_service.create_company.assert_called_once()

    def test_create_company_with_validation_error(
        self, test_client: TestClient, mock_company_service
    ):
        """Test company creation with invalid data."""
        # Arrange
        invalid_data = {"name": ""}  # Empty name should fail validation

        # Act
        response = test_client.post("/companies", json=invalid_data)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        mock_company_service.create_company.assert_not_called()

    def test_list_companies_success(
        self, test_client: TestClient, mock_company_service, sample_company_data
    ):
        """Test successful listing of companies."""
        # Arrange
        mock_company_service.get_all_companies.return_value = [sample_company_data]

        # Act
        response = test_client.get("/companies?skip=0&limit=10")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["name"] == "Test Company"
        mock_company_service.get_all_companies.assert_called_once_with(skip=0, limit=10)

    def test_list_companies_with_default_pagination(
        self, test_client: TestClient, mock_company_service, sample_company_data
    ):
        """Test listing companies with default pagination."""
        # Arrange
        mock_company_service.get_all_companies.return_value = [sample_company_data]

        # Act
        response = test_client.get("/companies")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        mock_company_service.get_all_companies.assert_called_once_with(skip=0, limit=100)

    def test_list_companies_with_invalid_pagination(self, test_client: TestClient):
        """Test listing companies with invalid pagination parameters."""
        # Arrange - negative skip value
        # Act
        response = test_client.get("/companies?skip=-1&limit=10")

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_company_by_id_success(
        self, test_client: TestClient, mock_company_service, sample_company_data
    ):
        """Test successful retrieval of company by ID."""
        # Arrange
        mock_company_service.get_company.return_value = sample_company_data

        # Act
        response = test_client.get("/companies/1")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == 1
        assert data["name"] == "Test Company"
        mock_company_service.get_company.assert_called_once_with(1)

    def test_get_company_by_id_not_found(self, test_client: TestClient, mock_company_service):
        """Test retrieval of non-existent company."""
        # Arrange
        from app.core.exceptions.api_exceptions import JSONFileNotFoundError

        mock_company_service.get_company.side_effect = JSONFileNotFoundError(
            filename="company_999.json"
        )

        # Act
        test_client.get("/companies/999")

        # Assert
        # The error will be handled by the middleware, check that service was called
        mock_company_service.get_company.assert_called_once_with(999)

    def test_get_company_by_ticker_success(
        self, test_client: TestClient, mock_company_service, sample_company_data
    ):
        """Test successful retrieval of company by ticker."""
        # Arrange
        mock_company_service.get_company_by_ticker.return_value = sample_company_data

        # Act
        response = test_client.get("/companies/ticker/TEST")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["primary_ticker"] == "TEST"
        mock_company_service.get_company_by_ticker.assert_called_once_with("TEST")

    def test_get_company_by_ticker_not_found(self, test_client: TestClient, mock_company_service):
        """Test retrieval of company with non-existent ticker."""
        # Arrange
        from app.core.exceptions.api_exceptions import JSONFileNotFoundError

        mock_company_service.get_company_by_ticker.side_effect = JSONFileNotFoundError(
            filename="company_XYZ.json"
        )

        # Act
        test_client.get("/companies/ticker/XYZ")

        # Assert
        mock_company_service.get_company_by_ticker.assert_called_once_with("XYZ")

    def test_update_company_success(
        self, test_client: TestClient, mock_company_service, sample_company_data
    ):
        """Test successful company update."""
        # Arrange
        updated_data = sample_company_data.model_copy(update={"name": "Updated Company Name"})
        mock_company_service.update_company.return_value = updated_data
        update_data = {"name": "Updated Company Name"}

        # Act
        response = test_client.put("/companies/1", json=update_data)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated Company Name"
        mock_company_service.update_company.assert_called_once()

    def test_update_company_with_partial_data(
        self, test_client: TestClient, mock_company_service, sample_company_data
    ):
        """Test company update with partial data."""
        # Arrange
        mock_company_service.update_company.return_value = sample_company_data
        update_data = {"primary_ticker": "UPDATED"}

        # Act
        response = test_client.put("/companies/1", json=update_data)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        mock_company_service.update_company.assert_called_once()

    def test_delete_company_success(self, test_client: TestClient, mock_company_service):
        """Test successful company deletion."""
        # Arrange
        mock_company_service.delete_company.return_value = None

        # Act
        response = test_client.delete("/companies/1")

        # Assert
        assert response.status_code == status.HTTP_204_NO_CONTENT
        mock_company_service.delete_company.assert_called_once_with(1)

    def test_delete_company_not_found(self, test_client: TestClient, mock_company_service):
        """Test deletion of non-existent company."""
        # Arrange
        from app.core.exceptions.api_exceptions import JSONFileNotFoundError

        mock_company_service.delete_company.side_effect = JSONFileNotFoundError(
            filename="company_999.json"
        )

        # Act
        test_client.delete("/companies/999")

        # Assert
        mock_company_service.delete_company.assert_called_once_with(999)

    def test_list_companies_with_limit_over_maximum(self, test_client: TestClient):
        """Test listing companies with limit exceeding maximum."""
        # Arrange - limit > 100 should fail validation
        # Act
        response = test_client.get("/companies?skip=0&limit=150")

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_company_with_tickers(
        self,
        test_client: TestClient,
        mock_company_service,
        sample_company_data,
    ):
        """Test company creation with multiple tickers."""
        # Arrange
        company_response = sample_company_data.model_copy(
            update={
                "tickers": [
                    {"exchange": "NYSE", "symbol": "TEST"},
                    {"exchange": "NASDAQ", "symbol": "TST"},
                ]
            }
        )
        mock_company_service.create_company.return_value = company_response
        company_data = {
            "name": "Test Company",
            "ir_url": "https://example.com/investor-relations",
            "primary_ticker": "TEST",
            "tickers": [
                {"exchange": "NYSE", "symbol": "TEST"},
                {"exchange": "NASDAQ", "symbol": "TST"},
            ],
        }

        # Act
        response = test_client.post("/companies", json=company_data)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert len(data["tickers"]) == 2
        mock_company_service.create_company.assert_called_once()

    def test_list_companies_with_zero_limit(self, test_client: TestClient):
        """Test listing companies with zero limit."""
        # Arrange - limit = 0 should fail validation
        # Act
        response = test_client.get("/companies?skip=0&limit=0")

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
