"""
Repository for Company model database operations.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

import json
from typing import Any

from psycopg_pool import AsyncConnectionPool

from app.db.repositories.base import BaseRepository


class CompanyRepository(BaseRepository):
    """Repository for managing Company database operations."""

    async def create(
        self,
        name: str,
        ir_url: str,
        primary_ticker: str | None = None,
        tickers: list[dict[str, str]] | None = None,
    ) -> dict[str, Any]:
        """Create a new company.

        Args:
            name: Company name.
            ir_url: Investor relations URL.
            primary_ticker: Primary stock ticker symbol.
            tickers: List of ticker dictionaries.

        Returns:
            Dictionary representing the created company.
        """
        query = """
            INSERT INTO companies (name, ir_url, primary_ticker, tickers)
            VALUES (%(name)s, %(ir_url)s, %(primary_ticker)s, %(tickers)s)
            RETURNING *
        """
        params = {
            "name": name,
            "ir_url": ir_url,
            "primary_ticker": primary_ticker,
            "tickers": json.dumps(tickers) if tickers else None,
        }
        return await self.execute_one(query, params)  # type: ignore

    async def get_by_id(self, company_id: int) -> dict[str, Any] | None:
        """Get company by ID.

        Args:
            company_id: Company ID.

        Returns:
            Dictionary representing the company, or None if not found.
        """
        query = "SELECT * FROM companies WHERE id = %(id)s"
        return await self.execute_one(query, {"id": company_id})

    async def get_by_ticker(self, ticker: str) -> dict[str, Any] | None:
        """Get company by ticker symbol.

        Args:
            ticker: Stock ticker symbol.

        Returns:
            Dictionary representing the company, or None if not found.
        """
        query = """
            SELECT * FROM companies
            WHERE primary_ticker = %(ticker)s
            OR tickers @> %(ticker_json)s::jsonb
        """
        ticker_json = json.dumps([{"ticker": ticker}])
        return await self.execute_one(query, {"ticker": ticker, "ticker_json": ticker_json})

    async def get_all(
        self, skip: int = 0, limit: int = 100
    ) -> list[dict[str, Any]]:
        """Get all companies with pagination.

        Args:
            skip: Number of records to skip.
            limit: Maximum number of records to return.

        Returns:
            List of dictionaries representing companies.
        """
        query = "SELECT * FROM companies ORDER BY id LIMIT %(limit)s OFFSET %(skip)s"
        return await self.execute_query(query, {"limit": limit, "skip": skip})

    async def update(
        self,
        company_id: int,
        name: str | None = None,
        ir_url: str | None = None,
        primary_ticker: str | None = None,
        tickers: list[dict[str, str]] | None = None,
    ) -> dict[str, Any] | None:
        """Update a company.

        Args:
            company_id: Company ID.
            name: Company name (optional).
            ir_url: Investor relations URL (optional).
            primary_ticker: Primary stock ticker symbol (optional).
            tickers: List of ticker dictionaries (optional).

        Returns:
            Dictionary representing the updated company, or None if not found.
        """
        updates = []
        params: dict[str, Any] = {"id": company_id}

        if name is not None:
            updates.append("name = %(name)s")
            params["name"] = name

        if ir_url is not None:
            updates.append("ir_url = %(ir_url)s")
            params["ir_url"] = ir_url

        if primary_ticker is not None:
            updates.append("primary_ticker = %(primary_ticker)s")
            params["primary_ticker"] = primary_ticker

        if tickers is not None:
            updates.append("tickers = %(tickers)s::jsonb")
            params["tickers"] = json.dumps(tickers)

        if not updates:
            return await self.get_by_id(company_id)

        query = f"""
            UPDATE companies
            SET {', '.join(updates)}
            WHERE id = %(id)s
            RETURNING *
        """
        return await self.execute_one(query, params)  # type: ignore

    async def delete(self, company_id: int) -> bool:
        """Delete a company by ID.

        Args:
            company_id: Company ID.

        Returns:
            True if company was deleted, False otherwise.
        """
        query = "DELETE FROM companies WHERE id = %(id)s"
        rows_affected = await self.execute_delete(query, {"id": company_id})
        return rows_affected > 0
