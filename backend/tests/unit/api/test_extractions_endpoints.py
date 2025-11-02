"""
Unit tests for Extractions API endpoints.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

import pytest
from fastapi import status
from fastapi.testclient import TestClient


@pytest.mark.unit
class TestExtractionsEndpoints:
    """Test cases for Extractions endpoints."""

    def test_create_extraction_success(
        self, test_client: TestClient, mock_extraction_service, sample_extraction_data
    ):
        """Test successful extraction creation."""
        # Arrange
        mock_extraction_service.create_extraction.return_value = sample_extraction_data
        extraction_data = {
            "document_id": 1,
            "statement_type": "Income Statement",
            "raw_data": {"revenue": 1000000, "expenses": 800000},
        }

        # Act
        response = test_client.post("/extractions", json=extraction_data)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["document_id"] == 1
        assert data["statement_type"] == "Income Statement"
        mock_extraction_service.create_extraction.assert_called_once()

    def test_create_extraction_with_empty_statement_type(
        self, test_client: TestClient, mock_extraction_service
    ):
        """Test extraction creation with empty statement type."""
        # Arrange
        invalid_data = {
            "document_id": 1,
            "statement_type": "",  # Empty should fail validation
            "raw_data": {"revenue": 1000000},
        }

        # Act
        response = test_client.post("/extractions", json=invalid_data)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_extraction_by_id_success(
        self, test_client: TestClient, mock_extraction_service, sample_extraction_data
    ):
        """Test successful retrieval of extraction by ID."""
        # Arrange
        mock_extraction_service.get_extraction.return_value = sample_extraction_data

        # Act
        response = test_client.get("/extractions/1")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == 1
        mock_extraction_service.get_extraction.assert_called_once_with(1)

    def test_get_extraction_by_id_not_found(
        self, test_client: TestClient, mock_extraction_service
    ):
        """Test retrieval of non-existent extraction."""
        # Arrange
        from app.core.exceptions.custom_exceptions import JSONFileNotFoundError
        mock_extraction_service.get_extraction.side_effect = JSONFileNotFoundError(
            filename="extraction_999.json"
        )

        # Act
        response = test_client.get("/extractions/999")

        # Assert
        mock_extraction_service.get_extraction.assert_called_once_with(999)

    def test_list_extractions_by_document_success(
        self, test_client: TestClient, mock_extraction_service, sample_extraction_data
    ):
        """Test successful listing of extractions by document."""
        # Arrange
        mock_extraction_service.get_extractions_by_document.return_value = [
            sample_extraction_data
        ]

        # Act
        response = test_client.get("/extractions/documents/1")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        mock_extraction_service.get_extractions_by_document.assert_called_once_with(1)

    def test_list_extractions_by_document_empty_result(
        self, test_client: TestClient, mock_extraction_service
    ):
        """Test listing extractions with empty result."""
        # Arrange
        mock_extraction_service.get_extractions_by_document.return_value = []

        # Act
        response = test_client.get("/extractions/documents/1")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data == []

    def test_get_extraction_by_document_and_type_success(
        self, test_client: TestClient, mock_extraction_service, sample_extraction_data
    ):
        """Test successful retrieval of extraction by document and type."""
        # Arrange
        mock_extraction_service.get_extraction_by_document_and_type.return_value = (
            sample_extraction_data
        )

        # Act
        response = test_client.get("/extractions/documents/1/statement-type/Income%20Statement")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["statement_type"] == "Income Statement"
        mock_extraction_service.get_extraction_by_document_and_type.assert_called_once_with(
            1, "Income Statement"
        )

    def test_get_extraction_by_document_and_type_not_found(
        self, test_client: TestClient, mock_extraction_service
    ):
        """Test retrieval with non-existent document and type."""
        # Arrange
        from app.core.exceptions.custom_exceptions import JSONFileNotFoundError
        mock_extraction_service.get_extraction_by_document_and_type.side_effect = (
            JSONFileNotFoundError(filename="extraction_not_found.json")
        )

        # Act
        response = test_client.get("/extractions/documents/999/statement-type/Cash%20Flow")

        # Assert
        mock_extraction_service.get_extraction_by_document_and_type.assert_called_once_with(
            999, "Cash Flow"
        )

    def test_update_extraction_success(
        self, test_client: TestClient, mock_extraction_service, sample_extraction_data
    ):
        """Test successful extraction update."""
        # Arrange
        updated_data = sample_extraction_data.copy()
        updated_data["raw_data"] = {"revenue": 1500000, "expenses": 1200000}
        mock_extraction_service.update_extraction.return_value = updated_data
        update_data = {"raw_data": {"revenue": 1500000, "expenses": 1200000}}

        # Act
        response = test_client.put("/extractions/1", json=update_data)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["raw_data"]["revenue"] == 1500000
        mock_extraction_service.update_extraction.assert_called_once()

    def test_update_extraction_with_partial_data(
        self, test_client: TestClient, mock_extraction_service, sample_extraction_data
    ):
        """Test extraction update with partial data."""
        # Arrange
        mock_extraction_service.update_extraction.return_value = sample_extraction_data
        update_data = {"raw_data": {"updated_field": "value"}}

        # Act
        response = test_client.put("/extractions/1", json=update_data)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        mock_extraction_service.update_extraction.assert_called_once()

    def test_delete_extraction_success(
        self, test_client: TestClient, mock_extraction_service
    ):
        """Test successful extraction deletion."""
        # Arrange
        mock_extraction_service.delete_extraction.return_value = None

        # Act
        response = test_client.delete("/extractions/1")

        # Assert
        assert response.status_code == status.HTTP_204_NO_CONTENT
        mock_extraction_service.delete_extraction.assert_called_once_with(1)

    def test_delete_extraction_not_found(
        self, test_client: TestClient, mock_extraction_service
    ):
        """Test deletion of non-existent extraction."""
        # Arrange
        from app.core.exceptions.custom_exceptions import JSONFileNotFoundError
        mock_extraction_service.delete_extraction.side_effect = JSONFileNotFoundError(
            filename="extraction_999.json"
        )

        # Act
        response = test_client.delete("/extractions/999")

        # Assert
        mock_extraction_service.delete_extraction.assert_called_once_with(999)

    def test_create_extraction_with_complex_raw_data(
        self, test_client: TestClient, mock_extraction_service, sample_extraction_data
    ):
        """Test extraction creation with complex raw data."""
        # Arrange
        sample_extraction_data["raw_data"] = {
            "income_statement": {
                "revenue": 1000000,
                "cogs": 600000,
                "gross_profit": 400000,
                "operating_expenses": {
                    "r_and_d": 100000,
                    "marketing": 50000,
                    "general_admin": 75000,
                },
                "operating_income": 175000,
                "net_income": 150000,
            }
        }
        mock_extraction_service.create_extraction.return_value = sample_extraction_data
        extraction_data = {
            "document_id": 1,
            "statement_type": "Income Statement",
            "raw_data": sample_extraction_data["raw_data"],
        }

        # Act
        response = test_client.post("/extractions", json=extraction_data)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "income_statement" in data["raw_data"]
        assert "operating_expenses" in data["raw_data"]["income_statement"]

    def test_list_extractions_multiple_results(
        self, test_client: TestClient, mock_extraction_service, sample_extraction_data
    ):
        """Test listing extractions with multiple results."""
        # Arrange
        extraction_2 = sample_extraction_data.copy()
        extraction_2["id"] = 2
        extraction_2["statement_type"] = "Balance Sheet"
        extraction_3 = sample_extraction_data.copy()
        extraction_3["id"] = 3
        extraction_3["statement_type"] = "Cash Flow Statement"
        mock_extraction_service.get_extractions_by_document.return_value = [
            sample_extraction_data,
            extraction_2,
            extraction_3,
        ]

        # Act
        response = test_client.get("/extractions/documents/1")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 3
        assert data[0]["statement_type"] == "Income Statement"
        assert data[1]["statement_type"] == "Balance Sheet"
        assert data[2]["statement_type"] == "Cash Flow Statement"

    def test_update_extraction_with_empty_raw_data(
        self, test_client: TestClient, mock_extraction_service, sample_extraction_data
    ):
        """Test extraction update with empty raw data."""
        # Arrange
        sample_extraction_data["raw_data"] = {}
        mock_extraction_service.update_extraction.return_value = sample_extraction_data
        update_data = {"raw_data": {}}

        # Act
        response = test_client.put("/extractions/1", json=update_data)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["raw_data"] == {}
