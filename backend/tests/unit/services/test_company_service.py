"""
Unit tests for CompanyService.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

import pytest

from app.core.exceptions.service_exceptions import (
    EntityNotFoundError,
    ServiceUnavailableError,
)
from app.schemas.company import CompanyCreate, CompanyUpdate
from app.services.company import CompanyService


@pytest.mark.unit
class TestCompanyService:
    """Test cases for CompanyService."""

    @pytest.mark.asyncio
    async def test_create_company_success(self, mock_company_repository, sample_company_data):
        """Test successful company creation."""
        # Arrange
        mock_company_repository.create.return_value = sample_company_data
        service = CompanyService(mock_company_repository)
        company_data = CompanyCreate(
            name="Test Company",
            ir_url="https://example.com/ir",
            primary_ticker="TEST",
        )

        # Act
        result = await service.create_company(company_data)

        # Assert
        assert result == sample_company_data
        mock_company_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_company_repository_returns_none(self, mock_company_repository):
        """Test company creation when repository returns None raises ServiceUnavailableError."""
        # Arrange
        # Note: In practice, repository.create() will never return None
        # This test maintains coverage for the edge case where a mock returns None
        mock_company_repository.create.return_value = None
        service = CompanyService(mock_company_repository)
        company_data = CompanyCreate(
            name="Test Company",
            ir_url="https://example.com/ir",
        )

        # Act & Assert
        with pytest.raises(ServiceUnavailableError) as exc_info:
            await service.create_company(company_data)

        assert "Unexpected error creating company" in str(exc_info.value)
        mock_company_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_company_repository_exception(self, mock_company_repository):
        """Test company creation when repository raises exception."""
        # Arrange
        mock_company_repository.create.side_effect = Exception("Database error")
        service = CompanyService(mock_company_repository)
        company_data = CompanyCreate(
            name="Test Company",
            ir_url="https://example.com/ir",
        )

        # Act & Assert
        with pytest.raises(ServiceUnavailableError) as exc_info:
            await service.create_company(company_data)

        assert "Unexpected error creating company" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_company_success(self, mock_company_repository, sample_company_data):
        """Test successful company retrieval by ID."""
        # Arrange
        mock_company_repository.get_by_id.return_value = sample_company_data
        service = CompanyService(mock_company_repository)

        # Act
        result = await service.get_company(1)

        # Assert
        assert result == sample_company_data
        mock_company_repository.get_by_id.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_get_company_not_found(self, mock_company_repository):
        """Test company retrieval when not found raises EntityNotFoundError."""
        # Arrange
        mock_company_repository.get_by_id.return_value = None
        service = CompanyService(mock_company_repository)

        # Act & Assert
        with pytest.raises(EntityNotFoundError) as exc_info:
            await service.get_company(999)

        assert exc_info.value.entity_name == "Company"
        assert exc_info.value.entity_id == 999

    @pytest.mark.asyncio
    async def test_get_company_by_ticker_success(
        self, mock_company_repository, sample_company_data
    ):
        """Test successful company retrieval by ticker."""
        # Arrange
        mock_company_repository.get_by_ticker.return_value = sample_company_data
        service = CompanyService(mock_company_repository)

        # Act
        result = await service.get_company_by_ticker("TEST")

        # Assert
        assert result == sample_company_data
        mock_company_repository.get_by_ticker.assert_called_once_with("TEST")

    @pytest.mark.asyncio
    async def test_get_company_by_ticker_not_found(self, mock_company_repository):
        """Test company retrieval by ticker when not found raises EntityNotFoundError."""
        # Arrange
        mock_company_repository.get_by_ticker.return_value = None
        service = CompanyService(mock_company_repository)

        # Act & Assert
        with pytest.raises(EntityNotFoundError) as exc_info:
            await service.get_company_by_ticker("NONEXISTENT")

        assert exc_info.value.entity_name == "Company"
        assert exc_info.value.entity_id == "NONEXISTENT"

    @pytest.mark.asyncio
    async def test_get_all_companies_success(self, mock_company_repository, sample_company_data):
        """Test successful retrieval of all companies."""
        # Arrange
        companies = [sample_company_data]
        mock_company_repository.get_all.return_value = companies
        service = CompanyService(mock_company_repository)

        # Act
        result = await service.get_all_companies(skip=0, limit=10)

        # Assert
        assert result == companies
        mock_company_repository.get_all.assert_called_once_with(skip=0, limit=10)

    @pytest.mark.asyncio
    async def test_update_company_success(self, mock_company_repository, sample_company_data):
        """Test successful company update."""
        # Arrange
        updated_data = sample_company_data.model_copy(update={"name": "Updated Company"})
        mock_company_repository.get_by_id.return_value = sample_company_data
        mock_company_repository.update.return_value = updated_data
        service = CompanyService(mock_company_repository)
        company_data = CompanyUpdate(name="Updated Company")

        # Act
        result = await service.update_company(1, company_data)

        # Assert
        assert result == updated_data
        assert result.name == "Updated Company"
        mock_company_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_company_not_found(self, mock_company_repository):
        """Test company update when company not found raises EntityNotFoundError."""
        # Arrange
        mock_company_repository.get_by_id.return_value = None
        service = CompanyService(mock_company_repository)
        company_data = CompanyUpdate(name="Updated Company")

        # Act & Assert
        with pytest.raises(EntityNotFoundError) as exc_info:
            await service.update_company(999, company_data)

        assert exc_info.value.entity_name == "Company"
        assert exc_info.value.entity_id == 999

    @pytest.mark.asyncio
    async def test_delete_company_success(self, mock_company_repository, sample_company_data):
        """Test successful company deletion."""
        # Arrange
        mock_company_repository.get_by_id.return_value = sample_company_data
        mock_company_repository.delete.return_value = True
        service = CompanyService(mock_company_repository)

        # Act
        result = await service.delete_company(1)

        # Assert
        assert result is None
        mock_company_repository.delete.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_delete_company_not_found(self, mock_company_repository):
        """Test company deletion when company not found raises EntityNotFoundError."""
        # Arrange
        mock_company_repository.get_by_id.return_value = None
        service = CompanyService(mock_company_repository)

        # Act & Assert
        with pytest.raises(EntityNotFoundError) as exc_info:
            await service.delete_company(999)

        assert exc_info.value.entity_name == "Company"
        assert exc_info.value.entity_id == 999

    @pytest.mark.asyncio
    async def test_delete_company_delete_fails(self, mock_company_repository, sample_company_data):
        """Test company deletion when delete operation fails raises ServiceUnavailableError."""
        # Arrange
        mock_company_repository.get_by_id.return_value = sample_company_data
        mock_company_repository.delete.return_value = False
        service = CompanyService(mock_company_repository)

        # Act & Assert
        with pytest.raises(ServiceUnavailableError) as exc_info:
            await service.delete_company(1)

        assert "Failed to delete company" in str(exc_info.value)
