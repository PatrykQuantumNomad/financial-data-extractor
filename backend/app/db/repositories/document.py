"""
Repository for Document model database operations.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

from typing import Any

from psycopg_pool import AsyncConnectionPool

from app.db.repositories.base import BaseRepository


class DocumentRepository(BaseRepository):
    """Repository for managing Document database operations."""

    async def create(
        self,
        company_id: int,
        url: str,
        fiscal_year: int,
        document_type: str,
        file_path: str | None = None,
    ) -> dict[str, Any]:
        """Create a new document.

        Args:
            company_id: ID of the company this document belongs to.
            url: URL where the document was found.
            fiscal_year: Fiscal year of the document.
            document_type: Type of document (e.g., 'annual_report', 'quarterly_report').
            file_path: Local file path if downloaded (optional).

        Returns:
            Dictionary representing the created document.
        """
        query = """
            INSERT INTO documents (company_id, url, fiscal_year, document_type, file_path)
            VALUES (%(company_id)s, %(url)s, %(fiscal_year)s, %(document_type)s, %(file_path)s)
            RETURNING *
        """
        params = {
            "company_id": company_id,
            "url": url,
            "fiscal_year": fiscal_year,
            "document_type": document_type,
            "file_path": file_path,
        }
        return await self.execute_one(query, params)  # type: ignore

    async def get_by_id(self, document_id: int) -> dict[str, Any] | None:
        """Get document by ID.

        Args:
            document_id: Document ID.

        Returns:
            Dictionary representing the document, or None if not found.
        """
        query = "SELECT * FROM documents WHERE id = %(id)s"
        return await self.execute_one(query, {"id": document_id})

    async def get_by_company(
        self,
        company_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Get all documents for a company with pagination.

        Args:
            company_id: Company ID.
            skip: Number of records to skip.
            limit: Maximum number of records to return.

        Returns:
            List of dictionaries representing documents.
        """
        query = """
            SELECT * FROM documents
            WHERE company_id = %(company_id)s
            ORDER BY fiscal_year DESC, created_at DESC
            LIMIT %(limit)s OFFSET %(skip)s
        """
        return await self.execute_query(
            query, {"company_id": company_id, "limit": limit, "skip": skip}
        )

    async def get_by_company_and_year(
        self, company_id: int, fiscal_year: int
    ) -> list[dict[str, Any]]:
        """Get documents for a company by fiscal year.

        Args:
            company_id: Company ID.
            fiscal_year: Fiscal year.

        Returns:
            List of dictionaries representing documents.
        """
        query = """
            SELECT * FROM documents
            WHERE company_id = %(company_id)s AND fiscal_year = %(fiscal_year)s
            ORDER BY created_at DESC
        """
        return await self.execute_query(
            query, {"company_id": company_id, "fiscal_year": fiscal_year}
        )

    async def get_by_company_and_type(
        self,
        company_id: int,
        document_type: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Get documents for a company by document type.

        Args:
            company_id: Company ID.
            document_type: Type of document.
            skip: Number of records to skip.
            limit: Maximum number of records to return.

        Returns:
            List of dictionaries representing documents.
        """
        query = """
            SELECT * FROM documents
            WHERE company_id = %(company_id)s AND document_type = %(document_type)s
            ORDER BY fiscal_year DESC, created_at DESC
            LIMIT %(limit)s OFFSET %(skip)s
        """
        return await self.execute_query(
            query,
            {
                "company_id": company_id,
                "document_type": document_type,
                "limit": limit,
                "skip": skip,
            },
        )

    async def update(
        self,
        document_id: int,
        url: str | None = None,
        fiscal_year: int | None = None,
        document_type: str | None = None,
        file_path: str | None = None,
    ) -> dict[str, Any] | None:
        """Update a document.

        Args:
            document_id: Document ID.
            url: URL where the document was found (optional).
            fiscal_year: Fiscal year of the document (optional).
            document_type: Type of document (optional).
            file_path: Local file path if downloaded (optional).

        Returns:
            Dictionary representing the updated document, or None if not found.
        """
        updates = []
        params: dict[str, Any] = {"id": document_id}

        if url is not None:
            updates.append("url = %(url)s")
            params["url"] = url

        if fiscal_year is not None:
            updates.append("fiscal_year = %(fiscal_year)s")
            params["fiscal_year"] = fiscal_year

        if document_type is not None:
            updates.append("document_type = %(document_type)s")
            params["document_type"] = document_type

        if file_path is not None:
            updates.append("file_path = %(file_path)s")
            params["file_path"] = file_path

        if not updates:
            return await self.get_by_id(document_id)

        query = f"""
            UPDATE documents
            SET {', '.join(updates)}
            WHERE id = %(id)s
            RETURNING *
        """
        return await self.execute_one(query, params)  # type: ignore

    async def delete(self, document_id: int) -> bool:
        """Delete a document by ID.

        Args:
            document_id: Document ID.

        Returns:
            True if document was deleted, False otherwise.
        """
        query = "DELETE FROM documents WHERE id = %(id)s"
        rows_affected = await self.execute_delete(query, {"id": document_id})
        return rows_affected > 0
