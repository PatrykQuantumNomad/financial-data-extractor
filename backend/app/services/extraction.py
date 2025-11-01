"""
Service for Extraction business logic.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

from typing import Any

from fastapi import HTTPException, status

from app.db.repositories.document import DocumentRepository
from app.db.repositories.extraction import ExtractionRepository
from app.schemas.extraction import ExtractionCreate, ExtractionUpdate


class ExtractionService:
    """Service for managing extraction business logic."""

    def __init__(
        self,
        extraction_repository: ExtractionRepository,
        document_repository: DocumentRepository,
    ):
        """Initialize service with repositories.

        Args:
            extraction_repository: Repository for extraction database operations.
            document_repository: Repository for document database operations.
        """
        self.extraction_repository = extraction_repository
        self.document_repository = document_repository

    async def create_extraction(
        self, extraction_data: ExtractionCreate
    ) -> dict[str, Any]:
        """Create a new extraction.

        Args:
            extraction_data: Extraction creation data.

        Returns:
            Dictionary representing the created extraction.

        Raises:
            HTTPException: If document not found or extraction creation fails.
        """
        # Verify document exists
        document = await self.document_repository.get_by_id(
            extraction_data.document_id
        )
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with id {extraction_data.document_id} not found",
            )

        try:
            extraction = await self.extraction_repository.create(
                document_id=extraction_data.document_id,
                statement_type=extraction_data.statement_type,
                raw_data=extraction_data.raw_data,
            )
            if not extraction:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create extraction",
                )
            return extraction
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating extraction: {str(e)}",
            ) from e

    async def get_extraction(self, extraction_id: int) -> dict[str, Any]:
        """Get extraction by ID.

        Args:
            extraction_id: Extraction ID.

        Returns:
            Dictionary representing the extraction.

        Raises:
            HTTPException: If extraction not found.
        """
        extraction = await self.extraction_repository.get_by_id(extraction_id)
        if not extraction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Extraction with id {extraction_id} not found",
            )
        return extraction

    async def get_extractions_by_document(
        self, document_id: int
    ) -> list[dict[str, Any]]:
        """Get all extractions for a document.

        Args:
            document_id: Document ID.

        Returns:
            List of dictionaries representing extractions.

        Raises:
            HTTPException: If document not found.
        """
        # Verify document exists
        document = await self.document_repository.get_by_id(document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with id {document_id} not found",
            )

        return await self.extraction_repository.get_by_document(document_id)

    async def get_extraction_by_document_and_type(
        self, document_id: int, statement_type: str
    ) -> dict[str, Any]:
        """Get extraction by document and statement type.

        Args:
            document_id: Document ID.
            statement_type: Type of financial statement.

        Returns:
            Dictionary representing the extraction.

        Raises:
            HTTPException: If document or extraction not found.
        """
        # Verify document exists
        document = await self.document_repository.get_by_id(document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with id {document_id} not found",
            )

        extraction = await self.extraction_repository.get_by_document_and_type(
            document_id, statement_type
        )
        if not extraction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"Extraction with document_id {document_id} "
                    f"and statement_type {statement_type} not found"
                ),
            )
        return extraction

    async def update_extraction(
        self, extraction_id: int, extraction_data: ExtractionUpdate
    ) -> dict[str, Any]:
        """Update an extraction.

        Args:
            extraction_id: Extraction ID.
            extraction_data: Extraction update data.

        Returns:
            Dictionary representing the updated extraction.

        Raises:
            HTTPException: If extraction not found or update fails.
        """
        # Check if extraction exists
        existing = await self.extraction_repository.get_by_id(extraction_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Extraction with id {extraction_id} not found",
            )

        try:
            extraction = await self.extraction_repository.update(
                extraction_id=extraction_id, raw_data=extraction_data.raw_data
            )
            if not extraction:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update extraction",
                )
            return extraction
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error updating extraction: {str(e)}",
            ) from e

    async def delete_extraction(self, extraction_id: int) -> None:
        """Delete an extraction by ID.

        Args:
            extraction_id: Extraction ID.

        Raises:
            HTTPException: If extraction not found or deletion fails.
        """
        # Check if extraction exists
        existing = await self.extraction_repository.get_by_id(extraction_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Extraction with id {extraction_id} not found",
            )

        deleted = await self.extraction_repository.delete(extraction_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete extraction",
            )
