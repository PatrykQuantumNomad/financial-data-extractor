"""
Service for Company business logic.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

from app.core.exceptions.db_exceptions import BaseDatabaseError
from app.core.exceptions.service_exceptions import EntityNotFoundError, ServiceUnavailableError
from app.core.exceptions.translators import translate_db_exception_to_service
from app.db.models.company import Company
from app.db.repositories.company import CompanyRepository
from app.schemas.company import CompanyCreate, CompanyDomain, CompanyUpdate


class CompanyService:
    """Service for managing company business logic."""

    def __init__(self, company_repository: CompanyRepository):
        """Initialize service with repository.

        Args:
            company_repository: Repository for company database operations.
        """
        self.repository = company_repository

    def _model_to_domain(self, company: Company) -> CompanyDomain:
        """Convert Company model to CompanyDomain schema.

        Args:
            company: Company model instance.

        Returns:
            CompanyDomain schema instance.
        """
        return CompanyDomain.model_validate(company)

    async def create_company(self, company_data: CompanyCreate) -> CompanyDomain:
        """Create a new company.

        Args:
            company_data: Company creation data.

        Returns:
            CompanyDomain representing the created company.

        Raises:
            ValidationError: If validation fails.
            ServiceUnavailableError: If database operation fails.
        """
        try:
            company = await self.repository.create(
                name=company_data.name,
                ir_url=company_data.ir_url,
                primary_ticker=company_data.primary_ticker,
                tickers=company_data.tickers,
            )
            return self._model_to_domain(company)
        except BaseDatabaseError as e:
            raise translate_db_exception_to_service(e) from e
        except Exception as e:
            raise ServiceUnavailableError(
                message=f"Unexpected error creating company: {str(e)}",
                service_name="company_service",
            ) from e

    async def get_company(self, company_id: int) -> CompanyDomain:
        """Get company by ID.

        Args:
            company_id: Company ID.

        Returns:
            CompanyDomain representing the company.

        Raises:
            EntityNotFoundError: If company not found.
            ServiceUnavailableError: If database operation fails.
        """
        try:
            company = await self.repository.get_by_id(company_id)
            if not company:
                raise EntityNotFoundError(entity_name="Company", entity_id=company_id)
            return self._model_to_domain(company)
        except BaseDatabaseError as e:
            raise translate_db_exception_to_service(e) from e

    async def get_company_by_ticker(self, ticker: str) -> CompanyDomain:
        """Get company by ticker symbol.

        Args:
            ticker: Stock ticker symbol.

        Returns:
            CompanyDomain representing the company.

        Raises:
            EntityNotFoundError: If company not found.
            ServiceUnavailableError: If database operation fails.
        """
        try:
            company = await self.repository.get_by_ticker(ticker)
            if not company:
                raise EntityNotFoundError(entity_name="Company", entity_id=ticker)
            return self._model_to_domain(company)
        except BaseDatabaseError as e:
            raise translate_db_exception_to_service(e) from e

    async def get_all_companies(self, skip: int = 0, limit: int = 100) -> list[CompanyDomain]:
        """Get all companies with pagination.

        Args:
            skip: Number of records to skip.
            limit: Maximum number of records to return.

        Returns:
            List of CompanyDomain representing companies.
        """
        companies = await self.repository.get_all(skip=skip, limit=limit)
        return [self._model_to_domain(company) for company in companies]

    async def update_company(self, company_id: int, company_data: CompanyUpdate) -> CompanyDomain:
        """Update a company.

        Args:
            company_id: Company ID.
            company_data: Company update data.

        Returns:
            CompanyDomain representing the updated company.

        Raises:
            EntityNotFoundError: If company not found.
            ValidationError: If validation fails.
            ServiceUnavailableError: If database operation fails.
        """
        try:
            # Check if company exists
            existing = await self.repository.get_by_id(company_id)
            if not existing:
                raise EntityNotFoundError(entity_name="Company", entity_id=company_id)

            company = await self.repository.update(
                company_id=company_id,
                name=company_data.name,
                ir_url=company_data.ir_url,
                primary_ticker=company_data.primary_ticker,
                tickers=company_data.tickers,
            )
            if not company:
                raise ServiceUnavailableError(
                    message="Failed to update company",
                    service_name="company_service",
                )
            return self._model_to_domain(company)
        except BaseDatabaseError as e:
            raise translate_db_exception_to_service(e) from e

    async def delete_company(self, company_id: int) -> None:
        """Delete a company by ID.

        Args:
            company_id: Company ID.

        Raises:
            EntityNotFoundError: If company not found.
            ServiceUnavailableError: If deletion fails.
        """
        try:
            # Check if company exists
            existing = await self.repository.get_by_id(company_id)
            if not existing:
                raise EntityNotFoundError(entity_name="Company", entity_id=company_id)

            deleted = await self.repository.delete(company_id)
            if not deleted:
                raise ServiceUnavailableError(
                    message="Failed to delete company",
                    service_name="company_service",
                )
        except BaseDatabaseError as e:
            raise translate_db_exception_to_service(e) from e
