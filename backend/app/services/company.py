"""
Service for Company business logic.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

from typing import Any

from fastapi import HTTPException, status

from app.db.repositories.company import CompanyRepository
from app.schemas.company import CompanyCreate, CompanyUpdate


class CompanyService:
    """Service for managing company business logic."""

    def __init__(self, company_repository: CompanyRepository):
        """Initialize service with repository.

        Args:
            company_repository: Repository for company database operations.
        """
        self.repository = company_repository

    async def create_company(self, company_data: CompanyCreate) -> dict[str, Any]:
        """Create a new company.

        Args:
            company_data: Company creation data.

        Returns:
            Dictionary representing the created company.

        Raises:
            HTTPException: If company creation fails.
        """
        try:
            company = await self.repository.create(
                name=company_data.name,
                ir_url=company_data.ir_url,
                primary_ticker=company_data.primary_ticker,
                tickers=company_data.tickers,
            )
            if not company:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create company",
                )
            return company
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating company: {str(e)}",
            ) from e

    async def get_company(self, company_id: int) -> dict[str, Any]:
        """Get company by ID.

        Args:
            company_id: Company ID.

        Returns:
            Dictionary representing the company.

        Raises:
            HTTPException: If company not found.
        """
        company = await self.repository.get_by_id(company_id)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company with id {company_id} not found",
            )
        return company

    async def get_company_by_ticker(self, ticker: str) -> dict[str, Any]:
        """Get company by ticker symbol.

        Args:
            ticker: Stock ticker symbol.

        Returns:
            Dictionary representing the company.

        Raises:
            HTTPException: If company not found.
        """
        company = await self.repository.get_by_ticker(ticker)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company with ticker {ticker} not found",
            )
        return company

    async def get_all_companies(
        self, skip: int = 0, limit: int = 100
    ) -> list[dict[str, Any]]:
        """Get all companies with pagination.

        Args:
            skip: Number of records to skip.
            limit: Maximum number of records to return.

        Returns:
            List of dictionaries representing companies.
        """
        return await self.repository.get_all(skip=skip, limit=limit)

    async def update_company(
        self, company_id: int, company_data: CompanyUpdate
    ) -> dict[str, Any]:
        """Update a company.

        Args:
            company_id: Company ID.
            company_data: Company update data.

        Returns:
            Dictionary representing the updated company.

        Raises:
            HTTPException: If company not found or update fails.
        """
        # Check if company exists
        existing = await self.repository.get_by_id(company_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company with id {company_id} not found",
            )

        try:
            company = await self.repository.update(
                company_id=company_id,
                name=company_data.name,
                ir_url=company_data.ir_url,
                primary_ticker=company_data.primary_ticker,
                tickers=company_data.tickers,
            )
            if not company:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update company",
                )
            return company
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error updating company: {str(e)}",
            ) from e

    async def delete_company(self, company_id: int) -> None:
        """Delete a company by ID.

        Args:
            company_id: Company ID.

        Raises:
            HTTPException: If company not found or deletion fails.
        """
        # Check if company exists
        existing = await self.repository.get_by_id(company_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company with id {company_id} not found",
            )

        deleted = await self.repository.delete(company_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete company",
            )
