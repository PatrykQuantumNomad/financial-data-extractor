"""
REST API endpoints for Document resource.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

from typing import Annotated
from urllib.parse import unquote

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from fastapi.responses import JSONResponse, Response

from app.core.storage import IStorageService
from app.schemas.document import DocumentCreate, DocumentResponse, DocumentUpdate
from app.services.dependencies import get_document_service, get_storage_service
from app.services.document import DocumentService

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post(
    "",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new document",
    description="Create a new document with the provided information.",
)
async def create_document(
    document_data: DocumentCreate,
    document_service: Annotated[DocumentService, Depends(get_document_service)],
) -> DocumentResponse:
    """Create a new document.

    Args:
        document_data: Document creation data.
        document_service: Document service (injected).

    Returns:
        Created document data.
    """
    document = await document_service.create_document(document_data)
    return document


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
    summary="Get document by ID",
    description="Get a specific document by its ID.",
)
async def get_document(
    document_id: Annotated[int, Path(description="Document ID")],
    document_service: Annotated[DocumentService, Depends(get_document_service)],
) -> DocumentResponse:
    """Get a document by ID.

    Args:
        document_id: Document ID.
        document_service: Document service (injected).

    Returns:
        Document data.
    """
    document = await document_service.get_document(document_id)
    return document


@router.get(
    "/companies/{company_id}",
    response_model=list[DocumentResponse],
    summary="List documents for a company",
    description="Get a paginated list of all documents for a specific company.",
)
async def list_documents_by_company(
    company_id: Annotated[int, Path(description="Company ID")],
    document_service: Annotated[DocumentService, Depends(get_document_service)],
    skip: Annotated[int, Query(ge=0, description="Number of records to skip")] = 0,
    limit: Annotated[
        int, Query(ge=1, le=100, description="Maximum number of records to return")
    ] = 100,
) -> list[DocumentResponse]:
    """List all documents for a company with pagination.

    Args:
        company_id: Company ID.
        skip: Number of records to skip.
        limit: Maximum number of records to return.
        document_service: Document service (injected).

    Returns:
        List of documents.
    """
    documents = await document_service.get_documents_by_company(
        company_id=company_id, skip=skip, limit=limit
    )
    return documents


@router.get(
    "/companies/{company_id}/fiscal-year/{fiscal_year}",
    response_model=list[DocumentResponse],
    summary="Get documents by company and fiscal year",
    description="Get all documents for a company by fiscal year.",
)
async def get_documents_by_company_and_year(
    company_id: Annotated[int, Path(description="Company ID")],
    fiscal_year: Annotated[int, Path(description="Fiscal year", ge=1900, le=2100)],
    document_service: Annotated[DocumentService, Depends(get_document_service)],
) -> list[DocumentResponse]:
    """Get documents for a company by fiscal year.

    Args:
        company_id: Company ID.
        fiscal_year: Fiscal year.
        document_service: Document service (injected).

    Returns:
        List of documents.
    """
    documents = await document_service.get_documents_by_company_and_year(
        company_id=company_id, fiscal_year=fiscal_year
    )
    return documents


@router.get(
    "/companies/{company_id}/type/{document_type}",
    response_model=list[DocumentResponse],
    summary="Get documents by company and type",
    description="Get all documents for a company by document type.",
)
async def get_documents_by_company_and_type(
    company_id: Annotated[int, Path(description="Company ID")],
    document_type: Annotated[str, Path(description="Document type")],
    document_service: Annotated[DocumentService, Depends(get_document_service)],
    skip: Annotated[int, Query(ge=0, description="Number of records to skip")] = 0,
    limit: Annotated[
        int, Query(ge=1, le=100, description="Maximum number of records to return")
    ] = 100,
) -> list[DocumentResponse]:
    """Get documents for a company by document type.

    Args:
        company_id: Company ID.
        document_type: Document type.
        skip: Number of records to skip.
        limit: Maximum number of records to return.
        document_service: Document service (injected).

    Returns:
        List of documents.
    """
    documents = await document_service.get_documents_by_company_and_type(
        company_id=company_id,
        document_type=document_type,
        skip=skip,
        limit=limit,
    )
    return documents


@router.put(
    "/{document_id}",
    response_model=DocumentResponse,
    summary="Update a document",
    description="Update an existing document with the provided information.",
)
async def update_document(
    document_id: Annotated[int, Path(description="Document ID")],
    document_data: DocumentUpdate,
    document_service: Annotated[DocumentService, Depends(get_document_service)],
) -> DocumentResponse:
    """Update a document.

    Args:
        document_id: Document ID.
        document_data: Document update data.
        document_service: Document service (injected).

    Returns:
        Updated document data.
    """
    document = await document_service.update_document(document_id, document_data)
    return document


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a document",
    description="Delete a document by its ID.",
)
async def delete_document(
    document_id: Annotated[int, Path(description="Document ID")],
    document_service: Annotated[DocumentService, Depends(get_document_service)],
) -> JSONResponse:
    """Delete a document.

    Args:
        document_id: Document ID.
        document_service: Document service (injected).

    Returns:
        Empty response with 204 status code.
    """
    await document_service.delete_document(document_id)
    return JSONResponse(content=None, status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/storage/companies/{company_id}",
    summary="List PDFs from storage for a company",
    description="List all PDF files stored in MinIO/local storage for a specific company. "
    "This queries storage directly, not the database.",
)
async def list_storage_pdfs_by_company(
    company_id: Annotated[int, Path(description="Company ID")],
    storage_service: Annotated[IStorageService, Depends(get_storage_service)],
    fiscal_year: Annotated[
        int | None, Query(description="Optional fiscal year filter", ge=1900, le=2100)
    ] = None,
) -> JSONResponse:
    """List all PDFs from storage for a company.

    Args:
        company_id: Company ID.
        storage_service: Storage service (injected).
        fiscal_year: Optional fiscal year to filter by.

    Returns:
        JSON response with list of PDF files from storage.
    """
    # Build prefix to filter files by company (and optionally by year)
    prefix = f"company_{company_id}"
    if fiscal_year:
        prefix = f"{prefix}/{fiscal_year}/"
    else:
        prefix = f"{prefix}/"

    files = await storage_service.list_files(prefix=prefix)

    # Format response with additional metadata
    result = {
        "company_id": company_id,
        "fiscal_year": fiscal_year,
        "prefix": prefix,
        "count": len(files),
        "files": files,
    }

    return JSONResponse(content=result, status_code=status.HTTP_200_OK)


@router.get(
    "/storage/download",
    summary="Download PDF from storage",
    description="Download a PDF file from MinIO/local storage by object key.",
    response_class=Response,
)
async def download_storage_pdf(
    object_key: Annotated[
        str, Query(description="Object key (path) of the file in storage")
    ],
    storage_service: Annotated[IStorageService, Depends(get_storage_service)],
) -> Response:
    """Download a PDF file from storage.

    Args:
        object_key: Object key (path) in storage.
        storage_service: Storage service (injected).

    Returns:
        PDF file as binary response.

    Raises:
        HTTPException: If file not found or retrieval fails.
    """
    try:
        # URL decode the object key in case it was encoded
        decoded_object_key = unquote(object_key)

        # Check if file exists
        if not await storage_service.file_exists(decoded_object_key):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"PDF file not found: {decoded_object_key}",
            )

        # Get file content
        file_content = await storage_service.get_file(decoded_object_key)

        # Extract filename from object key
        filename = decoded_object_key.split("/")[-1] or "document.pdf"

        # Return PDF file with proper headers
        return Response(
            content=file_content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'inline; filename="{filename}"',
                "Content-Length": str(len(file_content)),
            },
        )
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve PDF file: {str(e)}",
        ) from e
