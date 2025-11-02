"""
Repository for Company model database operations.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.exc import IntegrityError, OperationalError

from app.core.exceptions.db_exceptions import (
    DatabaseConnectionError,
    DatabaseIntegrityError,
    DatabaseTransactionError,
)
from app.db.models.company import Company
from app.db.repositories.base import BaseRepository


class CompanyRepository(BaseRepository):
    """Repository for managing Company database operations."""

    async def create(
        self,
        name: str,
        ir_url: str,
        primary_ticker: str | None = None,
        tickers: list[dict[str, str]] | None = None,
    ) -> Company:
        """Create a new company.

        Args:
            name: Company name.
            ir_url: Investor relations URL.
            primary_ticker: Primary stock ticker symbol.
            tickers: List of ticker dictionaries.

        Returns:
            Company model instance.

        Raises:
            DatabaseIntegrityError: If integrity constraint is violated.
            DatabaseConnectionError: If database connection fails.
            DatabaseTransactionError: If transaction fails.
        """
        try:
            company = Company(
                name=name,
                ir_url=ir_url,
                primary_ticker=primary_ticker,
                tickers=tickers,
            )
            self.session.add(company)
            await self.session.flush()
            await self.session.refresh(company)
            return company
        except IntegrityError as e:
            raise DatabaseIntegrityError(
                message=f"Failed to create company: {str(e.orig)}",
                entity_name="Company",
            ) from e
        except OperationalError as e:
            raise DatabaseConnectionError(
                message=f"Database connection error: {str(e.orig)}"
            ) from e
        except Exception as e:
            raise DatabaseTransactionError(message=f"Failed to create company: {str(e)}") from e

    async def get_by_id(self, company_id: int) -> Company | None:
        """Get company by ID.

        Args:
            company_id: Company ID.

        Returns:
            Company model instance, or None if not found.
        """
        return await self.session.get(Company, company_id)

    async def get_by_ticker(self, ticker: str) -> Company | None:
        """Get company by ticker symbol.

        Args:
            ticker: Stock ticker symbol.

        Returns:
            Company model instance, or None if not found.
        """
        # First try primary_ticker
        stmt = select(Company).where(Company.primary_ticker == ticker)
        result = await self.session.execute(stmt)
        company = result.scalar_one_or_none()

        if company is not None:
            return company

        # Then try JSONB tickers array
        stmt = select(Company).where(Company.tickers.contains([{"ticker": ticker}], type_=JSONB))
        result = await self.session.execute(stmt)
        company = result.scalar_one_or_none()

        return company

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[Company]:
        """Get all companies with pagination.

        Args:
            skip: Number of records to skip.
            limit: Maximum number of records to return.

        Returns:
            List of Company model instances.
        """
        stmt = select(Company).order_by(Company.id).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update(
        self,
        company_id: int,
        name: str | None = None,
        ir_url: str | None = None,
        primary_ticker: str | None = None,
        tickers: list[dict[str, str]] | None = None,
    ) -> Company | None:
        """Update a company.

        Args:
            company_id: Company ID.
            name: Company name (optional).
            ir_url: Investor relations URL (optional).
            primary_ticker: Primary stock ticker symbol (optional).
            tickers: List of ticker dictionaries (optional).

        Returns:
            Company model instance, or None if not found.

        Raises:
            DatabaseIntegrityError: If integrity constraint is violated.
            DatabaseConnectionError: If database connection fails.
            DatabaseTransactionError: If transaction fails.
        """
        company = await self.session.get(Company, company_id)
        if company is None:
            return None

        try:
            if name is not None:
                company.name = name
            if ir_url is not None:
                company.ir_url = ir_url
            if primary_ticker is not None:
                company.primary_ticker = primary_ticker
            if tickers is not None:
                company.tickers = tickers

            await self.session.flush()
            await self.session.refresh(company)
            return company
        except IntegrityError as e:
            raise DatabaseIntegrityError(
                message=f"Failed to update company: {str(e.orig)}",
                entity_name="Company",
            ) from e
        except OperationalError as e:
            raise DatabaseConnectionError(
                message=f"Database connection error: {str(e.orig)}"
            ) from e
        except Exception as e:
            raise DatabaseTransactionError(message=f"Failed to update company: {str(e)}") from e

    async def delete(self, company_id: int) -> bool:
        """Delete a company by ID.

        Args:
            company_id: Company ID.

        Returns:
            True if company was deleted, False otherwise.
        """
        company = await self.session.get(Company, company_id)
        if company is None:
            return False

        await self.session.delete(company)
        await self.session.flush()
        return True
