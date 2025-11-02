"""
Database dependency injection for FastAPI.

This module provides dependency functions for accessing the database
async sessions and repositories in FastAPI endpoints.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import AsyncSessionLocal
from app.db.repositories import (
    CompanyRepository,
    CompiledStatementRepository,
    DocumentRepository,
    ExtractionRepository,
)


async def get_db_session() -> AsyncGenerator[AsyncSession]:
    """Dependency function to get an async database session.

    Creates a new session per request and ensures it's closed after the request completes.

    Yields:
        AsyncSession: Async database session.

    Raises:
        RuntimeError: If database session cannot be created.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_company_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)]
) -> CompanyRepository:
    """Dependency function to get CompanyRepository instance.

    Args:
        session: Async database session (injected).

    Returns:
        CompanyRepository instance.
    """
    return CompanyRepository(session)


async def get_document_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)]
) -> DocumentRepository:
    """Dependency function to get DocumentRepository instance.

    Args:
        session: Async database session (injected).

    Returns:
        DocumentRepository instance.
    """
    return DocumentRepository(session)


async def get_extraction_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)]
) -> ExtractionRepository:
    """Dependency function to get ExtractionRepository instance.

    Args:
        session: Async database session (injected).

    Returns:
        ExtractionRepository instance.
    """
    return ExtractionRepository(session)


async def get_compiled_statement_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)]
) -> CompiledStatementRepository:
    """Dependency function to get CompiledStatementRepository instance.

    Args:
        session: Async database session (injected).

    Returns:
        CompiledStatementRepository instance.
    """
    return CompiledStatementRepository(session)
