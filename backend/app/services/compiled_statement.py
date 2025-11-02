"""
Service for CompiledStatement business logic.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

from fastapi import HTTPException, status

from app.db.models.extraction import CompiledStatement
from app.db.repositories.company import CompanyRepository
from app.db.repositories.compiled_statement import CompiledStatementRepository
from app.schemas.extraction import (
    CompiledStatementCreate,
    CompiledStatementResponse,
    CompiledStatementUpdate,
)


class CompiledStatementService:
    """Service for managing compiled statement business logic."""

    def __init__(
        self,
        compiled_statement_repository: CompiledStatementRepository,
        company_repository: CompanyRepository,
    ):
        """Initialize service with repositories.

        Args:
            compiled_statement_repository: Repository for compiled statement database operations.
            company_repository: Repository for company database operations.
        """
        self.compiled_statement_repository = compiled_statement_repository
        self.company_repository = company_repository

    def _model_to_response(
        self, compiled_statement: CompiledStatement
    ) -> CompiledStatementResponse:
        """Convert CompiledStatement model to CompiledStatementResponse schema.

        Args:
            compiled_statement: CompiledStatement model instance.

        Returns:
            CompiledStatementResponse schema instance.
        """
        return CompiledStatementResponse.model_validate(compiled_statement)

    async def create_compiled_statement(
        self, compiled_statement_data: CompiledStatementCreate
    ) -> CompiledStatementResponse:
        """Create a new compiled statement.

        Args:
            compiled_statement_data: Compiled statement creation data.

        Returns:
            CompiledStatementResponse representing the created compiled statement.

        Raises:
            HTTPException: If company not found or creation fails.
        """
        # Verify company exists
        company = await self.company_repository.get_by_id(compiled_statement_data.company_id)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(f"Company with id {compiled_statement_data.company_id} not found"),
            )

        try:
            compiled_statement = await self.compiled_statement_repository.upsert(
                company_id=compiled_statement_data.company_id,
                statement_type=compiled_statement_data.statement_type,
                data=compiled_statement_data.data,
            )
            return self._model_to_response(compiled_statement)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating compiled statement: {str(e)}",
            ) from e

    async def get_compiled_statement(self, compiled_statement_id: int) -> CompiledStatementResponse:
        """Get compiled statement by ID.

        Args:
            compiled_statement_id: Compiled statement ID.

        Returns:
            CompiledStatementResponse representing the compiled statement.

        Raises:
            HTTPException: If compiled statement not found.
        """
        compiled_statement = await self.compiled_statement_repository.get_by_id(
            compiled_statement_id
        )
        if not compiled_statement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(f"Compiled statement with id {compiled_statement_id} not found"),
            )
        return self._model_to_response(compiled_statement)

    async def get_compiled_statements_by_company(
        self, company_id: int
    ) -> list[CompiledStatementResponse]:
        """Get all compiled statements for a company.

        Args:
            company_id: Company ID.

        Returns:
            List of CompiledStatementResponse representing compiled statements.

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

        compiled_statements = await self.compiled_statement_repository.get_by_company(company_id)
        return [self._model_to_response(stmt) for stmt in compiled_statements]

    async def get_compiled_statement_by_company_and_type(
        self, company_id: int, statement_type: str
    ) -> CompiledStatementResponse:
        """Get compiled statement by company and statement type.

        Args:
            company_id: Company ID.
            statement_type: Type of financial statement.

        Returns:
            CompiledStatementResponse representing the compiled statement.

        Raises:
            HTTPException: If company or compiled statement not found.
        """
        # Verify company exists
        company = await self.company_repository.get_by_id(company_id)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company with id {company_id} not found",
            )

        compiled_statement = await self.compiled_statement_repository.get_by_company_and_type(
            company_id, statement_type
        )
        if not compiled_statement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"Compiled statement with company_id {company_id} "
                    f"and statement_type {statement_type} not found"
                ),
            )
        return self._model_to_response(compiled_statement)

    async def update_compiled_statement(
        self,
        compiled_statement_id: int,
        compiled_statement_data: CompiledStatementUpdate,
    ) -> CompiledStatementResponse:
        """Update a compiled statement.

        Args:
            compiled_statement_id: Compiled statement ID.
            compiled_statement_data: Compiled statement update data.

        Returns:
            CompiledStatementResponse representing the updated compiled statement.

        Raises:
            HTTPException: If compiled statement not found or update fails.
        """
        # Check if compiled statement exists
        existing = await self.compiled_statement_repository.get_by_id(compiled_statement_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(f"Compiled statement with id {compiled_statement_id} not found"),
            )

        try:
            compiled_statement = await self.compiled_statement_repository.update(
                compiled_statement_id=compiled_statement_id,
                data=compiled_statement_data.data,
            )
            if not compiled_statement:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update compiled statement",
                )
            return self._model_to_response(compiled_statement)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error updating compiled statement: {str(e)}",
            ) from e

    async def upsert_compiled_statement(
        self, compiled_statement_data: CompiledStatementCreate
    ) -> CompiledStatementResponse:
        """Insert or update a compiled statement.

        Args:
            compiled_statement_data: Compiled statement data.

        Returns:
            CompiledStatementResponse representing the compiled statement.

        Raises:
            HTTPException: If company not found or upsert fails.
        """
        # Verify company exists
        company = await self.company_repository.get_by_id(compiled_statement_data.company_id)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(f"Company with id {compiled_statement_data.company_id} not found"),
            )

        try:
            compiled_statement = await self.compiled_statement_repository.upsert(
                company_id=compiled_statement_data.company_id,
                statement_type=compiled_statement_data.statement_type,
                data=compiled_statement_data.data,
            )
            return self._model_to_response(compiled_statement)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error upserting compiled statement: {str(e)}",
            ) from e

    async def delete_compiled_statement(self, compiled_statement_id: int) -> None:
        """Delete a compiled statement by ID.

        Args:
            compiled_statement_id: Compiled statement ID.

        Raises:
            HTTPException: If compiled statement not found or deletion fails.
        """
        # Check if compiled statement exists
        existing = await self.compiled_statement_repository.get_by_id(compiled_statement_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(f"Compiled statement with id {compiled_statement_id} not found"),
            )

        deleted = await self.compiled_statement_repository.delete(compiled_statement_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete compiled statement",
            )
