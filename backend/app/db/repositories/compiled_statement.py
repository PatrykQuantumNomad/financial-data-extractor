"""
Repository for CompiledStatement model database operations.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

from typing import Any

from sqlalchemy import select

from app.db.models.extraction import CompiledStatement
from app.db.repositories.base import BaseRepository


class CompiledStatementRepository(BaseRepository):
    """Repository for managing CompiledStatement database operations."""

    async def create(
        self,
        company_id: int,
        statement_type: str,
        data: dict[str, Any],
    ) -> CompiledStatement:
        """Create a new compiled statement.

        Args:
            company_id: ID of the company this compiled statement belongs to.
            statement_type: Type of financial statement (e.g., 'income_statement', 'balance_sheet').
            data: Compiled financial data as dictionary.

        Returns:
            CompiledStatement model instance.
        """
        compiled_statement = CompiledStatement(
            company_id=company_id,
            statement_type=statement_type,
            data=data,
        )
        self.session.add(compiled_statement)
        await self.session.flush()
        await self.session.refresh(compiled_statement)
        return compiled_statement

    async def get_by_id(self, compiled_statement_id: int) -> CompiledStatement | None:
        """Get compiled statement by ID.

        Args:
            compiled_statement_id: Compiled statement ID.

        Returns:
            CompiledStatement model instance, or None if not found.
        """
        return await self.session.get(CompiledStatement, compiled_statement_id)

    async def get_by_company(self, company_id: int) -> list[CompiledStatement]:
        """Get all compiled statements for a company.

        Args:
            company_id: Company ID.

        Returns:
            List of CompiledStatement model instances.
        """
        stmt = (
            select(CompiledStatement)
            .where(CompiledStatement.company_id == company_id)
            .order_by(CompiledStatement.statement_type)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_company_and_type(
        self, company_id: int, statement_type: str
    ) -> CompiledStatement | None:
        """Get compiled statement by company and statement type.

        Args:
            company_id: Company ID.
            statement_type: Type of financial statement.

        Returns:
            CompiledStatement model instance, or None if not found.
        """
        stmt = select(CompiledStatement).where(
            CompiledStatement.company_id == company_id,
            CompiledStatement.statement_type == statement_type,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update(
        self,
        compiled_statement_id: int,
        data: dict[str, Any] | None = None,
    ) -> CompiledStatement | None:
        """Update a compiled statement.

        Args:
            compiled_statement_id: Compiled statement ID.
            data: Compiled financial data as dictionary (optional).

        Returns:
            CompiledStatement model instance, or None if not found.
        """
        compiled_statement = await self.session.get(CompiledStatement, compiled_statement_id)
        if compiled_statement is None:
            return None

        if data is not None:
            compiled_statement.data = data

        await self.session.flush()
        await self.session.refresh(compiled_statement)
        return compiled_statement

    async def upsert(
        self,
        company_id: int,
        statement_type: str,
        data: dict[str, Any],
    ) -> CompiledStatement:
        """Insert or update a compiled statement.

        If a compiled statement exists for the company and statement type, it will be updated.
        Otherwise, a new one will be created.

        Args:
            company_id: ID of the company this compiled statement belongs to.
            statement_type: Type of financial statement.
            data: Compiled financial data as dictionary.

        Returns:
            CompiledStatement model instance.
        """
        # Try to get existing statement using direct query to get model
        stmt = select(CompiledStatement).where(
            CompiledStatement.company_id == company_id,
            CompiledStatement.statement_type == statement_type,
        )
        result = await self.session.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing is not None:
            # Update existing
            existing.data = data
            await self.session.flush()
            await self.session.refresh(existing)
            return existing

        # Create new
        return await self.create(company_id, statement_type, data)

    async def delete(self, compiled_statement_id: int) -> bool:
        """Delete a compiled statement by ID.

        Args:
            compiled_statement_id: Compiled statement ID.

        Returns:
            True if compiled statement was deleted, False otherwise.
        """
        compiled_statement = await self.session.get(CompiledStatement, compiled_statement_id)
        if compiled_statement is None:
            return False

        await self.session.delete(compiled_statement)
        await self.session.flush()
        return True
