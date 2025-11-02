"""
Repository for Extraction model database operations.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

from typing import Any

from sqlalchemy import select

from app.db.models.extraction import Extraction
from app.db.repositories.base import BaseRepository


class ExtractionRepository(BaseRepository):
    """Repository for managing Extraction database operations."""

    async def create(
        self,
        document_id: int,
        statement_type: str,
        raw_data: dict[str, Any],
    ) -> Extraction:
        """Create a new extraction.

        Args:
            document_id: ID of the document this extraction belongs to.
            statement_type: Type of financial statement (e.g., 'income_statement', 'balance_sheet').
            raw_data: Raw extracted data as dictionary.

        Returns:
            Extraction model instance.
        """
        extraction = Extraction(
            document_id=document_id,
            statement_type=statement_type,
            raw_data=raw_data,
        )
        self.session.add(extraction)
        await self.session.flush()
        await self.session.refresh(extraction)
        return extraction

    async def get_by_id(self, extraction_id: int) -> Extraction | None:
        """Get extraction by ID.

        Args:
            extraction_id: Extraction ID.

        Returns:
            Extraction model instance, or None if not found.
        """
        return await self.session.get(Extraction, extraction_id)

    async def get_by_document(self, document_id: int) -> list[Extraction]:
        """Get all extractions for a document.

        Args:
            document_id: Document ID.

        Returns:
            List of Extraction model instances.
        """
        stmt = (
            select(Extraction)
            .where(Extraction.document_id == document_id)
            .order_by(Extraction.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_document_and_type(
        self, document_id: int, statement_type: str
    ) -> Extraction | None:
        """Get extraction by document and statement type.

        Args:
            document_id: Document ID.
            statement_type: Type of financial statement.

        Returns:
            Extraction model instance, or None if not found.
        """
        stmt = (
            select(Extraction)
            .where(
                Extraction.document_id == document_id,
                Extraction.statement_type == statement_type,
            )
            .order_by(Extraction.created_at.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update(
        self,
        extraction_id: int,
        raw_data: dict[str, Any] | None = None,
    ) -> Extraction | None:
        """Update an extraction.

        Args:
            extraction_id: Extraction ID.
            raw_data: Raw extracted data as dictionary (optional).

        Returns:
            Extraction model instance, or None if not found.
        """
        extraction = await self.session.get(Extraction, extraction_id)
        if extraction is None:
            return None

        if raw_data is not None:
            extraction.raw_data = raw_data

        await self.session.flush()
        await self.session.refresh(extraction)
        return extraction

    async def delete(self, extraction_id: int) -> bool:
        """Delete an extraction by ID.

        Args:
            extraction_id: Extraction ID.

        Returns:
            True if extraction was deleted, False otherwise.
        """
        extraction = await self.session.get(Extraction, extraction_id)
        if extraction is None:
            return False

        await self.session.delete(extraction)
        await self.session.flush()
        return True
