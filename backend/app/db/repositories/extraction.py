"""
Repository for Extraction model database operations.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

import json
from typing import Any

from psycopg_pool import AsyncConnectionPool

from app.db.repositories.base import BaseRepository


class ExtractionRepository(BaseRepository):
    """Repository for managing Extraction database operations."""

    async def create(
        self,
        document_id: int,
        statement_type: str,
        raw_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Create a new extraction.

        Args:
            document_id: ID of the document this extraction belongs to.
            statement_type: Type of financial statement (e.g., 'income_statement', 'balance_sheet').
            raw_data: Raw extracted data as dictionary.

        Returns:
            Dictionary representing the created extraction.
        """
        query = """
            INSERT INTO extractions (document_id, statement_type, raw_data)
            VALUES (%(document_id)s, %(statement_type)s, %(raw_data)s::jsonb)
            RETURNING *
        """
        params = {
            "document_id": document_id,
            "statement_type": statement_type,
            "raw_data": json.dumps(raw_data),
        }
        return await self.execute_one(query, params)  # type: ignore

    async def get_by_id(self, extraction_id: int) -> dict[str, Any] | None:
        """Get extraction by ID.

        Args:
            extraction_id: Extraction ID.

        Returns:
            Dictionary representing the extraction, or None if not found.
        """
        query = "SELECT * FROM extractions WHERE id = %(id)s"
        return await self.execute_one(query, {"id": extraction_id})

    async def get_by_document(
        self, document_id: int
    ) -> list[dict[str, Any]]:
        """Get all extractions for a document.

        Args:
            document_id: Document ID.

        Returns:
            List of dictionaries representing extractions.
        """
        query = """
            SELECT * FROM extractions
            WHERE document_id = %(document_id)s
            ORDER BY created_at DESC
        """
        return await self.execute_query(query, {"document_id": document_id})

    async def get_by_document_and_type(
        self, document_id: int, statement_type: str
    ) -> dict[str, Any] | None:
        """Get extraction by document and statement type.

        Args:
            document_id: Document ID.
            statement_type: Type of financial statement.

        Returns:
            Dictionary representing the extraction, or None if not found.
        """
        query = """
            SELECT * FROM extractions
            WHERE document_id = %(document_id)s AND statement_type = %(statement_type)s
            ORDER BY created_at DESC
            LIMIT 1
        """
        return await self.execute_one(
            query, {"document_id": document_id, "statement_type": statement_type}
        )

    async def update(
        self,
        extraction_id: int,
        raw_data: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        """Update an extraction.

        Args:
            extraction_id: Extraction ID.
            raw_data: Raw extracted data as dictionary (optional).

        Returns:
            Dictionary representing the updated extraction, or None if not found.
        """
        if raw_data is None:
            return await self.get_by_id(extraction_id)

        query = """
            UPDATE extractions
            SET raw_data = %(raw_data)s::jsonb
            WHERE id = %(id)s
            RETURNING *
        """
        params = {
            "id": extraction_id,
            "raw_data": json.dumps(raw_data),
        }
        return await self.execute_one(query, params)  # type: ignore

    async def delete(self, extraction_id: int) -> bool:
        """Delete an extraction by ID.

        Args:
            extraction_id: Extraction ID.

        Returns:
            True if extraction was deleted, False otherwise.
        """
        query = "DELETE FROM extractions WHERE id = %(id)s"
        rows_affected = await self.execute_delete(query, {"id": extraction_id})
        return rows_affected > 0
