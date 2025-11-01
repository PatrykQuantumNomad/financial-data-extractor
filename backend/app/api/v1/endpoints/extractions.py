"""
REST API endpoints for Extraction resource.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, status
from fastapi.responses import JSONResponse

from app.schemas.extraction import (
    ExtractionCreate,
    ExtractionResponse,
    ExtractionUpdate,
)
from app.services.dependencies import get_extraction_service
from app.services.extraction import ExtractionService

router = APIRouter(prefix="/extractions", tags=["Extractions"])


@router.post(
    "",
    response_model=ExtractionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new extraction",
    description="Create a new extraction with the provided information.",
)
async def create_extraction(
    extraction_data: ExtractionCreate,
    extraction_service: Annotated[
        ExtractionService, Depends(get_extraction_service)
    ],
) -> ExtractionResponse:
    """Create a new extraction.

    Args:
        extraction_data: Extraction creation data.
        extraction_service: Extraction service (injected).

    Returns:
        Created extraction data.
    """
    extraction = await extraction_service.create_extraction(extraction_data)
    return ExtractionResponse(**extraction)


@router.get(
    "/{extraction-id}",
    response_model=ExtractionResponse,
    summary="Get extraction by ID",
    description="Get a specific extraction by its ID.",
)
async def get_extraction(
    extraction_id: Annotated[int, Path(description="Extraction ID")],
    extraction_service: Annotated[
        ExtractionService, Depends(get_extraction_service)
    ],
) -> ExtractionResponse:
    """Get an extraction by ID.

    Args:
        extraction_id: Extraction ID.
        extraction_service: Extraction service (injected).

    Returns:
        Extraction data.
    """
    extraction = await extraction_service.get_extraction(extraction_id)
    return ExtractionResponse(**extraction)


@router.get(
    "/documents/{document-id}",
    response_model=list[ExtractionResponse],
    summary="List extractions for a document",
    description="Get all extractions for a specific document.",
)
async def list_extractions_by_document(
    document_id: Annotated[int, Path(description="Document ID")],
    extraction_service: Annotated[
        ExtractionService, Depends(get_extraction_service)
    ],
) -> list[ExtractionResponse]:
    """List all extractions for a document.

    Args:
        document_id: Document ID.
        extraction_service: Extraction service (injected).

    Returns:
        List of extractions.
    """
    extractions = await extraction_service.get_extractions_by_document(document_id)
    return [ExtractionResponse(**ext) for ext in extractions]


@router.get(
    "/documents/{document-id}/statement-type/{statement-type}",
    response_model=ExtractionResponse,
    summary="Get extraction by document and statement type",
    description="Get an extraction for a document by statement type.",
)
async def get_extraction_by_document_and_type(
    document_id: Annotated[int, Path(description="Document ID")],
    statement_type: Annotated[str, Path(description="Statement type")],
    extraction_service: Annotated[
        ExtractionService, Depends(get_extraction_service)
    ],
) -> ExtractionResponse:
    """Get an extraction by document and statement type.

    Args:
        document_id: Document ID.
        statement_type: Statement type.
        extraction_service: Extraction service (injected).

    Returns:
        Extraction data.
    """
    extraction = await extraction_service.get_extraction_by_document_and_type(
        document_id, statement_type
    )
    return ExtractionResponse(**extraction)


@router.put(
    "/{extraction-id}",
    response_model=ExtractionResponse,
    summary="Update an extraction",
    description="Update an existing extraction with the provided information.",
)
async def update_extraction(
    extraction_id: Annotated[int, Path(description="Extraction ID")],
    extraction_data: ExtractionUpdate,
    extraction_service: Annotated[
        ExtractionService, Depends(get_extraction_service)
    ],
) -> ExtractionResponse:
    """Update an extraction.

    Args:
        extraction_id: Extraction ID.
        extraction_data: Extraction update data.
        extraction_service: Extraction service (injected).

    Returns:
        Updated extraction data.
    """
    extraction = await extraction_service.update_extraction(
        extraction_id, extraction_data
    )
    return ExtractionResponse(**extraction)


@router.delete(
    "/{extraction-id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an extraction",
    description="Delete an extraction by its ID.",
)
async def delete_extraction(
    extraction_id: Annotated[int, Path(description="Extraction ID")],
    extraction_service: Annotated[
        ExtractionService, Depends(get_extraction_service)
    ],
) -> JSONResponse:
    """Delete an extraction.

    Args:
        extraction_id: Extraction ID.
        extraction_service: Extraction service (injected).

    Returns:
        Empty response with 204 status code.
    """
    await extraction_service.delete_extraction(extraction_id)
    return JSONResponse(content=None, status_code=status.HTTP_204_NO_CONTENT)
