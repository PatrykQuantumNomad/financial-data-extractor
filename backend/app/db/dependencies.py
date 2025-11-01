"""
Database dependency injection for FastAPI.

This module provides dependency functions for accessing the database
connection pool in FastAPI endpoints.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

from typing import Annotated

from fastapi import Depends, Request
from psycopg_pool import AsyncConnectionPool

from app.db.repositories import (
    CompanyRepository,
    CompiledStatementRepository,
    DocumentRepository,
    ExtractionRepository,
)


async def get_db_pool(request: Request) -> AsyncConnectionPool:
    """Dependency function to get the database connection pool from FastAPI app state.

    Args:
        request: FastAPI request object.

    Returns:
        Async connection pool for database operations.

    Raises:
        RuntimeError: If database pool is not available in app state.
    """
    pool: AsyncConnectionPool | None = getattr(request.app.state, "db_pool", None)
    if pool is None:
        raise RuntimeError("Database connection pool not initialized")
    return pool


async def get_company_repository(
    db_pool: Annotated[AsyncConnectionPool, Depends(get_db_pool)]
) -> CompanyRepository:
    """Dependency function to get CompanyRepository instance.

    Args:
        db_pool: Database connection pool (injected).

    Returns:
        CompanyRepository instance.
    """
    return CompanyRepository(db_pool)


async def get_document_repository(
    db_pool: Annotated[AsyncConnectionPool, Depends(get_db_pool)]
) -> DocumentRepository:
    """Dependency function to get DocumentRepository instance.

    Args:
        db_pool: Database connection pool (injected).

    Returns:
        DocumentRepository instance.
    """
    return DocumentRepository(db_pool)


async def get_extraction_repository(
    db_pool: Annotated[AsyncConnectionPool, Depends(get_db_pool)]
) -> ExtractionRepository:
    """Dependency function to get ExtractionRepository instance.

    Args:
        db_pool: Database connection pool (injected).

    Returns:
        ExtractionRepository instance.
    """
    return ExtractionRepository(db_pool)


async def get_compiled_statement_repository(
    db_pool: Annotated[AsyncConnectionPool, Depends(get_db_pool)]
) -> CompiledStatementRepository:
    """Dependency function to get CompiledStatementRepository instance.

    Args:
        db_pool: Database connection pool (injected).

    Returns:
        CompiledStatementRepository instance.
    """
    return CompiledStatementRepository(db_pool)
