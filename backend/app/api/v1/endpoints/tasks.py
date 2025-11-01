"""
REST API endpoints for triggering and managing Celery tasks.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

from typing import Annotated

from app.tasks.extraction_tasks import (extract_financial_statements,
                                        process_document)
from app.tasks.orchestration_tasks import (extract_company_financial_data,
                                           recompile_company_statements)
from app.tasks.scraping_tasks import (classify_document, download_pdf,
                                      scrape_investor_relations)
from fastapi import APIRouter, Depends, HTTPException, Path, status
from pydantic import BaseModel, Field

router = APIRouter(prefix="/tasks", tags=["Tasks"])


class TaskResponse(BaseModel):
    """Response model for task trigger endpoints."""

    task_id: str = Field(..., description="Celery task ID")
    status: str = Field(..., description="Task status")
    message: str = Field(..., description="Human-readable message")


class TaskStatusResponse(BaseModel):
    """Response model for task status check."""

    task_id: str = Field(..., description="Celery task ID")
    status: str = Field(..., description="Task status")
    result: dict | None = Field(None, description="Task result if completed")
    error: str | None = Field(None, description="Error message if failed")


@router.post(
    "/companies/{company_id}/extract",
    response_model=TaskResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger company financial data extraction",
    description="Triggers the complete financial data extraction workflow for a company. "
    "This includes scraping, downloading, extracting, and compiling financial statements.",
)
async def trigger_extract_company_financial_data(
    company_id: Annotated[int, Path(description="Company ID")],
) -> TaskResponse:
    """Trigger financial data extraction for a company.

    This is the main orchestration task that:
    1. Scrapes investor relations website
    2. Discovers and classifies documents
    3. Downloads PDFs
    4. Extracts financial statements
    5. Normalizes and compiles statements

    Args:
        company_id: ID of the company to extract data for.

    Returns:
        Task response with task ID and status.
    """
    try:
        task = extract_company_financial_data.delay(company_id)
        return TaskResponse(
            task_id=task.id,
            status="PENDING",
            message=f"Financial data extraction started for company {company_id}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger extraction task: {str(e)}",
        ) from e


@router.post(
    "/companies/{company_id}/scrape",
    response_model=TaskResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger investor relations scraping",
    description="Scrapes the investor relations website to discover PDF documents.",
)
async def trigger_scrape_investor_relations(
    company_id: Annotated[int, Path(description="Company ID")],
) -> TaskResponse:
    """Trigger scraping of investor relations website.

    Args:
        company_id: ID of the company to scrape.

    Returns:
        Task response with task ID and status.
    """
    try:
        task = scrape_investor_relations.delay(company_id)
        return TaskResponse(
            task_id=task.id,
            status="PENDING",
            message=f"Scraping started for company {company_id}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger scraping task: {str(e)}",
        ) from e


@router.post(
    "/documents/{document_id}/download",
    response_model=TaskResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger PDF download",
    description="Downloads a PDF document from its URL and stores it locally.",
)
async def trigger_download_pdf(
    document_id: Annotated[int, Path(description="Document ID")],
) -> TaskResponse:
    """Trigger PDF download task.

    Args:
        document_id: ID of the document to download.

    Returns:
        Task response with task ID and status.
    """
    try:
        task = download_pdf.delay(document_id)
        return TaskResponse(
            task_id=task.id,
            status="PENDING",
            message=f"PDF download started for document {document_id}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger download task: {str(e)}",
        ) from e


@router.post(
    "/documents/{document_id}/classify",
    response_model=TaskResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger document classification",
    description="Classifies a document by type (annual report, quarterly, etc.).",
)
async def trigger_classify_document(
    document_id: Annotated[int, Path(description="Document ID")],
) -> TaskResponse:
    """Trigger document classification task.

    Args:
        document_id: ID of the document to classify.

    Returns:
        Task response with task ID and status.
    """
    try:
        task = classify_document.delay(document_id)
        return TaskResponse(
            task_id=task.id,
            status="PENDING",
            message=f"Classification started for document {document_id}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger classification task: {str(e)}",
        ) from e


@router.post(
    "/documents/{document_id}/extract",
    response_model=TaskResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger financial statement extraction",
    description="Extracts financial statements from a PDF document using LLM.",
)
async def trigger_extract_financial_statements(
    document_id: Annotated[int, Path(description="Document ID")],
) -> TaskResponse:
    """Trigger financial statement extraction task.

    Args:
        document_id: ID of the document to extract from.

    Returns:
        Task response with task ID and status.
    """
    try:
        task = extract_financial_statements.delay(document_id)
        return TaskResponse(
            task_id=task.id,
            status="PENDING",
            message=f"Financial statement extraction started for document {document_id}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger extraction task: {str(e)}",
        ) from e


@router.post(
    "/documents/{document_id}/process",
    response_model=TaskResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Process document end-to-end",
    description="Processes a document through all steps: classify, download, and extract.",
)
async def trigger_process_document(
    document_id: Annotated[int, Path(description="Document ID")],
) -> TaskResponse:
    """Trigger end-to-end document processing task.

    Args:
        document_id: ID of the document to process.

    Returns:
        Task response with task ID and status.
    """
    try:
        task = process_document.delay(document_id)
        return TaskResponse(
            task_id=task.id,
            status="PENDING",
            message=f"Document processing started for document {document_id}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger processing task: {str(e)}",
        ) from e


@router.post(
    "/companies/{company_id}/recompile",
    response_model=TaskResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Recompile company statements",
    description="Recompiles all financial statements for a company after new extractions.",
)
async def trigger_recompile_company_statements(
    company_id: Annotated[int, Path(description="Company ID")],
) -> TaskResponse:
    """Trigger recompilation of company statements.

    Args:
        company_id: ID of the company.

    Returns:
        Task response with task ID and status.
    """
    try:
        task = recompile_company_statements.delay(company_id)
        return TaskResponse(
            task_id=task.id,
            status="PENDING",
            message=f"Statement recompilation started for company {company_id}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger recompilation task: {str(e)}",
        ) from e


@router.get(
    "/{task_id}",
    response_model=TaskStatusResponse,
    summary="Get task status",
    description="Get the current status and result of a Celery task.",
)
async def get_task_status(
    task_id: Annotated[str, Path(description="Celery task ID")],
) -> TaskStatusResponse:
    """Get task status by task ID.

    Args:
        task_id: Celery task ID.

    Returns:
        Task status response with current state and result.
    """
    from app.tasks.celery_app import celery_app

    try:
        result = celery_app.AsyncResult(task_id)
        task_status = result.state

        response_data = {
            "task_id": task_id,
            "status": task_status,
            "result": None,
            "error": None,
        }

        if task_status == "SUCCESS":
            response_data["result"] = result.get()
        elif task_status == "FAILURE":
            try:
                response_data["error"] = str(result.info)
            except Exception:
                response_data["error"] = "Task failed with unknown error"

        return TaskStatusResponse(**response_data)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get task status: {str(e)}",
        ) from e
