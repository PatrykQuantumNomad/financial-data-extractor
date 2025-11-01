"""
REST API endpoints for CompiledStatement resource.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, status
from fastapi.responses import JSONResponse

from app.schemas.extraction import (
    CompiledStatementCreate,
    CompiledStatementResponse,
    CompiledStatementUpdate,
)
from app.services.compiled_statement import CompiledStatementService
from app.services.dependencies import get_compiled_statement_service

router = APIRouter(
    prefix="/compiled-statements", tags=["Compiled Statements"]
)


@router.post(
    "",
    response_model=CompiledStatementResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create or update a compiled statement",
    description="Create a new compiled statement or update if it already exists.",
)
async def create_or_update_compiled_statement(
    compiled_statement_data: CompiledStatementCreate,
    compiled_statement_service: Annotated[
        CompiledStatementService, Depends(get_compiled_statement_service)
    ],
) -> CompiledStatementResponse:
    """Create or update a compiled statement.

    Args:
        compiled_statement_data: Compiled statement data.
        compiled_statement_service: Compiled statement service (injected).

    Returns:
        Compiled statement data.
    """
    compiled_statement = (
        await compiled_statement_service.upsert_compiled_statement(
            compiled_statement_data
        )
    )
    return CompiledStatementResponse(**compiled_statement)


@router.get(
    "/{compiled-statement-id}",
    response_model=CompiledStatementResponse,
    summary="Get compiled statement by ID",
    description="Get a specific compiled statement by its ID.",
)
async def get_compiled_statement(
    compiled_statement_id: Annotated[
        int, Path(description="Compiled statement ID")
    ],
    compiled_statement_service: Annotated[
        CompiledStatementService, Depends(get_compiled_statement_service)
    ],
) -> CompiledStatementResponse:
    """Get a compiled statement by ID.

    Args:
        compiled_statement_id: Compiled statement ID.
        compiled_statement_service: Compiled statement service (injected).

    Returns:
        Compiled statement data.
    """
    compiled_statement = await compiled_statement_service.get_compiled_statement(
        compiled_statement_id
    )
    return CompiledStatementResponse(**compiled_statement)


@router.get(
    "/companies/{company-id}",
    response_model=list[CompiledStatementResponse],
    summary="List compiled statements for a company",
    description="Get all compiled statements for a specific company.",
)
async def list_compiled_statements_by_company(
    company_id: Annotated[int, Path(description="Company ID")],
    compiled_statement_service: Annotated[
        CompiledStatementService, Depends(get_compiled_statement_service)
    ],
) -> list[CompiledStatementResponse]:
    """List all compiled statements for a company.

    Args:
        company_id: Company ID.
        compiled_statement_service: Compiled statement service (injected).

    Returns:
        List of compiled statements.
    """
    compiled_statements = (
        await compiled_statement_service.get_compiled_statements_by_company(
            company_id
        )
    )
    return [
        CompiledStatementResponse(**cs) for cs in compiled_statements
    ]


@router.get(
    "/companies/{company-id}/statement-type/{statement-type}",
    response_model=CompiledStatementResponse,
    summary="Get compiled statement by company and statement type",
    description="Get a compiled statement for a company by statement type.",
)
async def get_compiled_statement_by_company_and_type(
    company_id: Annotated[int, Path(description="Company ID")],
    statement_type: Annotated[str, Path(description="Statement type")],
    compiled_statement_service: Annotated[
        CompiledStatementService, Depends(get_compiled_statement_service)
    ],
) -> CompiledStatementResponse:
    """Get a compiled statement by company and statement type.

    Args:
        company_id: Company ID.
        statement_type: Statement type.
        compiled_statement_service: Compiled statement service (injected).

    Returns:
        Compiled statement data.
    """
    compiled_statement = (
        await compiled_statement_service.get_compiled_statement_by_company_and_type(
            company_id, statement_type
        )
    )
    return CompiledStatementResponse(**compiled_statement)


@router.put(
    "/{compiled-statement-id}",
    response_model=CompiledStatementResponse,
    summary="Update a compiled statement",
    description="Update an existing compiled statement with the provided information.",
)
async def update_compiled_statement(
    compiled_statement_id: Annotated[
        int, Path(description="Compiled statement ID")
    ],
    compiled_statement_data: CompiledStatementUpdate,
    compiled_statement_service: Annotated[
        CompiledStatementService, Depends(get_compiled_statement_service)
    ],
) -> CompiledStatementResponse:
    """Update a compiled statement.

    Args:
        compiled_statement_id: Compiled statement ID.
        compiled_statement_data: Compiled statement update data.
        compiled_statement_service: Compiled statement service (injected).

    Returns:
        Updated compiled statement data.
    """
    compiled_statement = (
        await compiled_statement_service.update_compiled_statement(
            compiled_statement_id, compiled_statement_data
        )
    )
    return CompiledStatementResponse(**compiled_statement)


@router.delete(
    "/{compiled-statement-id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a compiled statement",
    description="Delete a compiled statement by its ID.",
)
async def delete_compiled_statement(
    compiled_statement_id: Annotated[
        int, Path(description="Compiled statement ID")
    ],
    compiled_statement_service: Annotated[
        CompiledStatementService, Depends(get_compiled_statement_service)
    ],
) -> JSONResponse:
    """Delete a compiled statement.

    Args:
        compiled_statement_id: Compiled statement ID.
        compiled_statement_service: Compiled statement service (injected).

    Returns:
        Empty response with 204 status code.
    """
    await compiled_statement_service.delete_compiled_statement(
        compiled_statement_id
    )
    return JSONResponse(content=None, status_code=status.HTTP_204_NO_CONTENT)
