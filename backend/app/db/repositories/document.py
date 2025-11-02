"""
Repository for Document model database operations.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

from sqlalchemy import select

from app.db.models.document import Document
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
    ) -> Document:
        """Create a new document.

        Args:
            company_id: ID of the company this document belongs to.
            url: URL where the document was found.
            fiscal_year: Fiscal year of the document.
            document_type: Type of document (e.g., 'annual_report', 'quarterly_report').
            file_path: Local file path if downloaded (optional).

        Returns:
            Document model instance.
        """
        document = Document(
            company_id=company_id,
            url=url,
            fiscal_year=fiscal_year,
            document_type=document_type,
            file_path=file_path,
        )
        self.session.add(document)
        await self.session.flush()
        await self.session.refresh(document)
        return document

    async def get_by_id(self, document_id: int) -> Document | None:
        """Get document by ID.

        Args:
            document_id: Document ID.

        Returns:
            Document model instance, or None if not found.
        """
        return await self.session.get(Document, document_id)

    async def get_by_company(
        self,
        company_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Document]:
        """Get all documents for a company with pagination.

        Args:
            company_id: Company ID.
            skip: Number of records to skip.
            limit: Maximum number of records to return.

        Returns:
            List of Document model instances.
        """
        stmt = (
            select(Document)
            .where(Document.company_id == company_id)
            .order_by(Document.fiscal_year.desc(), Document.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_company_and_year(self, company_id: int, fiscal_year: int) -> list[Document]:
        """Get documents for a company by fiscal year.

        Args:
            company_id: Company ID.
            fiscal_year: Fiscal year.

        Returns:
            List of Document model instances.
        """
        stmt = (
            select(Document)
            .where(Document.company_id == company_id, Document.fiscal_year == fiscal_year)
            .order_by(Document.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_company_and_type(
        self,
        company_id: int,
        document_type: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Document]:
        """Get documents for a company by document type.

        Args:
            company_id: Company ID.
            document_type: Type of document.
            skip: Number of records to skip.
            limit: Maximum number of records to return.

        Returns:
            List of Document model instances.
        """
        stmt = (
            select(Document)
            .where(
                Document.company_id == company_id,
                Document.document_type == document_type,
            )
            .order_by(Document.fiscal_year.desc(), Document.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update(
        self,
        document_id: int,
        url: str | None = None,
        fiscal_year: int | None = None,
        document_type: str | None = None,
        file_path: str | None = None,
    ) -> Document | None:
        """Update a document.

        Args:
            document_id: Document ID.
            url: URL where the document was found (optional).
            fiscal_year: Fiscal year of the document (optional).
            document_type: Type of document (optional).
            file_path: Local file path if downloaded (optional).

        Returns:
            Document model instance, or None if not found.
        """
        document = await self.session.get(Document, document_id)
        if document is None:
            return None

        if url is not None:
            document.url = url
        if fiscal_year is not None:
            document.fiscal_year = fiscal_year
        if document_type is not None:
            document.document_type = document_type
        if file_path is not None:
            document.file_path = file_path

        await self.session.flush()
        await self.session.refresh(document)
        return document

    async def delete(self, document_id: int) -> bool:
        """Delete a document by ID.

        Args:
            document_id: Document ID.

        Returns:
            True if document was deleted, False otherwise.
        """
        document = await self.session.get(Document, document_id)
        if document is None:
            return False

        await self.session.delete(document)
        await self.session.flush()
        return True
