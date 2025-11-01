"""
Service for Document business logic.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

from typing import Any

from fastapi import HTTPException, status

from app.db.repositories.company import CompanyRepository
from app.db.repositories.document import DocumentRepository
from app.schemas.document import DocumentCreate, DocumentUpdate


class DocumentService:
    """Service for managing document business logic."""

    def __init__(
        self,
        document_repository: DocumentRepository,
        company_repository: CompanyRepository,
    ):
        """Initialize service with repositories.

        Args:
            document_repository: Repository for document database operations.
            company_repository: Repository for company database operations.
        """
        self.document_repository = document_repository
        self.company_repository = company_repository

    async def create_document(
        self, document_data: DocumentCreate
    ) -> dict[str, Any]:
        """Create a new document.

        Args:
            document_data: Document creation data.

        Returns:
            Dictionary representing the created document.

        Raises:
            HTTPException: If company not found or document creation fails.
        """
        # Verify company exists
        company = await self.company_repository.get_by_id(document_data.company_id)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company with id {document_data.company_id} not found",
            )

        try:
            document = await self.document_repository.create(
                company_id=document_data.company_id,
                url=document_data.url,
                fiscal_year=document_data.fiscal_year,
                document_type=document_data.document_type,
                file_path=document_data.file_path,
            )
            if not document:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create document",
                )
            return document
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating document: {str(e)}",
            ) from e

    async def get_document(self, document_id: int) -> dict[str, Any]:
        """Get document by ID.

        Args:
            document_id: Document ID.

        Returns:
            Dictionary representing the document.

        Raises:
            HTTPException: If document not found.
        """
        document = await self.document_repository.get_by_id(document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with id {document_id} not found",
            )
        return document

    async def get_documents_by_company(
        self, company_id: int, skip: int = 0, limit: int = 100
    ) -> list[dict[str, Any]]:
        """Get all documents for a company with pagination.

        Args:
            company_id: Company ID.
            skip: Number of records to skip.
            limit: Maximum number of records to return.

        Returns:
            List of dictionaries representing documents.

        Raises:
            HTTPException: If company not found.
        """
        # Verify company exists
        company = await self.company_repository.get_by_id(company_id)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company with id {company_id} not found",
            )

        return await self.document_repository.get_by_company(
            company_id=company_id, skip=skip, limit=limit
        )

    async def get_documents_by_company_and_year(
        self, company_id: int, fiscal_year: int
    ) -> list[dict[str, Any]]:
        """Get documents for a company by fiscal year.

        Args:
            company_id: Company ID.
            fiscal_year: Fiscal year.

        Returns:
            List of dictionaries representing documents.

        Raises:
            HTTPException: If company not found.
        """
        # Verify company exists
        company = await self.company_repository.get_by_id(company_id)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company with id {company_id} not found",
            )

        return await self.document_repository.get_by_company_and_year(
            company_id=company_id, fiscal_year=fiscal_year
        )

    async def get_documents_by_company_and_type(
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

        Raises:
            HTTPException: If company not found.
        """
        # Verify company exists
        company = await self.company_repository.get_by_id(company_id)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company with id {company_id} not found",
            )

        return await self.document_repository.get_by_company_and_type(
            company_id=company_id,
            document_type=document_type,
            skip=skip,
            limit=limit,
        )

    async def update_document(
        self, document_id: int, document_data: DocumentUpdate
    ) -> dict[str, Any]:
        """Update a document.

        Args:
            document_id: Document ID.
            document_data: Document update data.

        Returns:
            Dictionary representing the updated document.

        Raises:
            HTTPException: If document not found or update fails.
        """
        # Check if document exists
        existing = await self.document_repository.get_by_id(document_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with id {document_id} not found",
            )

        try:
            document = await self.document_repository.update(
                document_id=document_id,
                url=document_data.url,
                fiscal_year=document_data.fiscal_year,
                document_type=document_data.document_type,
                file_path=document_data.file_path,
            )
            if not document:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update document",
                )
            return document
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error updating document: {str(e)}",
            ) from e

    async def delete_document(self, document_id: int) -> None:
        """Delete a document by ID.

        Args:
            document_id: Document ID.

        Raises:
            HTTPException: If document not found or deletion fails.
        """
        # Check if document exists
        existing = await self.document_repository.get_by_id(document_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with id {document_id} not found",
            )

        deleted = await self.document_repository.delete(document_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete document",
            )
