"""
Service dependency injection for FastAPI.

This module provides dependency functions for accessing service layer
in FastAPI endpoints.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

from typing import TYPE_CHECKING, Annotated

from app.db.dependencies import (get_company_repository,
                                 get_compiled_statement_repository,
                                 get_document_repository,
                                 get_extraction_repository)
# Runtime imports needed for type annotations
from app.db.repositories.company import CompanyRepository
from app.db.repositories.compiled_statement import CompiledStatementRepository
from app.db.repositories.document import DocumentRepository
from app.db.repositories.extraction import ExtractionRepository
from app.services.company import CompanyService
from app.services.compiled_statement import CompiledStatementService
from app.services.document import DocumentService
from app.services.extraction import ExtractionService
from fastapi import Depends


async def get_company_service(
    company_repository: Annotated[
        CompanyRepository, Depends(get_company_repository)
    ],
) -> CompanyService:
    """Dependency function to get CompanyService instance.

    Args:
        company_repository: Company repository (injected).

    Returns:
        CompanyService instance.
    """
    return CompanyService(company_repository)


async def get_document_service(
    document_repository: Annotated[
        DocumentRepository, Depends(get_document_repository)
    ],
    company_repository: Annotated[
        CompanyRepository, Depends(get_company_repository)
    ],
) -> DocumentService:
    """Dependency function to get DocumentService instance.

    Args:
        document_repository: Document repository (injected).
        company_repository: Company repository (injected).

    Returns:
        DocumentService instance.
    """
    return DocumentService(document_repository, company_repository)


async def get_extraction_service(
    extraction_repository: Annotated[
        ExtractionRepository, Depends(get_extraction_repository)
    ],
    document_repository: Annotated[
        DocumentRepository, Depends(get_document_repository)
    ],
) -> ExtractionService:
    """Dependency function to get ExtractionService instance.

    Args:
        extraction_repository: Extraction repository (injected).
        document_repository: Document repository (injected).

    Returns:
        ExtractionService instance.
    """
    return ExtractionService(extraction_repository, document_repository)


async def get_compiled_statement_service(
    compiled_statement_repository: Annotated[
        CompiledStatementRepository, Depends(get_compiled_statement_repository)
    ],
    company_repository: Annotated[
        CompanyRepository, Depends(get_company_repository)
    ],
) -> CompiledStatementService:
    """Dependency function to get CompiledStatementService instance.

    Args:
        compiled_statement_repository: Compiled statement repository (injected).
        company_repository: Company repository (injected).

    Returns:
        CompiledStatementService instance.
    """
    return CompiledStatementService(
        compiled_statement_repository, company_repository
    )
