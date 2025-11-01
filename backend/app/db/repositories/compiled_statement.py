"""
Repository for CompiledStatement model database operations.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

import json
from typing import Any

from psycopg_pool import AsyncConnectionPool

from app.db.repositories.base import BaseRepository


class CompiledStatementRepository(BaseRepository):
    """Repository for managing CompiledStatement database operations."""

    async def create(
        self,
        company_id: int,
        statement_type: str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """Create a new compiled statement.

        Args:
            company_id: ID of the company this compiled statement belongs to.
            statement_type: Type of financial statement (e.g., 'income_statement', 'balance_sheet').
            data: Compiled financial data as dictionary.

        Returns:
            Dictionary representing the created compiled statement.
        """
        query = """
            INSERT INTO compiled_statements (company_id, statement_type, data)
            VALUES (%(company_id)s, %(statement_type)s, %(data)s::jsonb)
            RETURNING *
        """
        params = {
            "company_id": company_id,
            "statement_type": statement_type,
            "data": json.dumps(data),
        }
        return await self.execute_one(query, params)  # type: ignore

    async def get_by_id(
        self, compiled_statement_id: int
    ) -> dict[str, Any] | None:
        """Get compiled statement by ID.

        Args:
            compiled_statement_id: Compiled statement ID.

        Returns:
            Dictionary representing the compiled statement, or None if not found.
        """
        query = "SELECT * FROM compiled_statements WHERE id = %(id)s"
        return await self.execute_one(query, {"id": compiled_statement_id})

    async def get_by_company(
        self, company_id: int
    ) -> list[dict[str, Any]]:
        """Get all compiled statements for a company.

        Args:
            company_id: Company ID.

        Returns:
            List of dictionaries representing compiled statements.
        """
        query = """
            SELECT * FROM compiled_statements
            WHERE company_id = %(company_id)s
            ORDER BY statement_type
        """
        return await self.execute_query(query, {"company_id": company_id})

    async def get_by_company_and_type(
        self, company_id: int, statement_type: str
    ) -> dict[str, Any] | None:
        """Get compiled statement by company and statement type.

        Args:
            company_id: Company ID.
            statement_type: Type of financial statement.

        Returns:
            Dictionary representing the compiled statement, or None if not found.
        """
        query = """
            SELECT * FROM compiled_statements
            WHERE company_id = %(company_id)s AND statement_type = %(statement_type)s
        """
        return await self.execute_one(
            query, {"company_id": company_id, "statement_type": statement_type}
        )

    async def update(
        self,
        compiled_statement_id: int,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        """Update a compiled statement.

        Args:
            compiled_statement_id: Compiled statement ID.
            data: Compiled financial data as dictionary (optional).

        Returns:
            Dictionary representing the updated compiled statement, or None if not found.
        """
        if data is None:
            return await self.get_by_id(compiled_statement_id)

        query = """
            UPDATE compiled_statements
            SET data = %(data)s::jsonb, updated_at = NOW()
            WHERE id = %(id)s
            RETURNING *
        """
        params = {
            "id": compiled_statement_id,
            "data": json.dumps(data),
        }
        return await self.execute_one(query, params)  # type: ignore

    async def upsert(
        self,
        company_id: int,
        statement_type: str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """Insert or update a compiled statement.

        If a compiled statement exists for the company and statement type, it will be updated.
        Otherwise, a new one will be created.

        Args:
            company_id: ID of the company this compiled statement belongs to.
            statement_type: Type of financial statement.
            data: Compiled financial data as dictionary.

        Returns:
            Dictionary representing the compiled statement.
        """
        query = """
            INSERT INTO compiled_statements (company_id, statement_type, data)
            VALUES (%(company_id)s, %(statement_type)s, %(data)s::jsonb)
            ON CONFLICT (company_id, statement_type)
            DO UPDATE SET
                data = EXCLUDED.data,
                updated_at = NOW()
            RETURNING *
        """
        params = {
            "company_id": company_id,
            "statement_type": statement_type,
            "data": json.dumps(data),
        }
        return await self.execute_one(query, params)  # type: ignore

    async def delete(self, compiled_statement_id: int) -> bool:
        """Delete a compiled statement by ID.

        Args:
            compiled_statement_id: Compiled statement ID.

        Returns:
            True if compiled statement was deleted, False otherwise.
        """
        query = "DELETE FROM compiled_statements WHERE id = %(id)s"
        rows_affected = await self.execute_delete(
            query, {"id": compiled_statement_id}
        )
        return rows_affected > 0
