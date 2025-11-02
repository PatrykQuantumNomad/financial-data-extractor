"""
Celery tasks for web scraping and document discovery.

Tasks are thin wrappers around worker classes that handle business logic.
This separation allows testing business logic without Celery infrastructure.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

import logging
from typing import Any

import httpx
from celery import Task

from app.tasks.celery_app import celery_app
from app.tasks.progress import CeleryProgressCallback
from app.tasks.utils import get_db_context, run_async, validate_task_result
from app.workers.scraping_worker import ScrapingWorker
from config import Settings

logger = logging.getLogger(__name__)


@celery_app.task(
    bind=True,
    name="app.tasks.scraping_tasks.scrape_investor_relations",
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(httpx.HTTPError, httpx.TimeoutException, ConnectionError),
)
def scrape_investor_relations(self: Task, company_id: int) -> dict[str, Any]:
    """Scrape investor relations website to discover PDF documents.

    Args:
        company_id: ID of the company to scrape.

    Returns:
        Dictionary with task results including discovered documents.

    Raises:
        ValueError: If company not found or scraping fails.
    """
    task_id = self.request.id
    logger.info(
        "Starting scrape_investor_relations task",
        extra={
            "task_id": task_id,
            "company_id": company_id,
        },
    )

    try:
        # Create progress callback for worker
        progress_callback = CeleryProgressCallback(self)

        # Create worker with database session
        async def _execute_worker():
            async with get_db_context() as session:
                worker = ScrapingWorker(session, progress_callback)
                settings = Settings()
                return await worker.scrape_investor_relations(company_id, settings.openai_api_key)

        result = run_async(_execute_worker())

        # Add task_id to result for consistency
        result["task_id"] = task_id

        validate_task_result(result, ["task_id", "company_id", "status"])
        logger.info(
            "Completed scrape_investor_relations task",
            extra={"task_id": task_id, "result": result},
        )

        return result

    except httpx.HTTPStatusError as e:
        # Handle 403 Forbidden specifically - don't retry, just log and return empty results
        if e.response.status_code == 403:
            logger.warning(
                f"403 Forbidden when scraping {company_id} - website blocking requests",
                extra={"task_id": task_id, "company_id": company_id},
            )
            # Return empty results instead of failing
            return {
                "task_id": task_id,
                "company_id": company_id,
                "status": "partial",
                "message": "Website returned 403 Forbidden - no documents discovered",
                "discovered_count": 0,
                "created_count": 0,
                "documents": [],
            }
        # For other HTTP errors, retry
        logger.error(
            f"HTTP error in scrape_investor_relations task: {e}",
            extra={
                "task_id": task_id,
                "company_id": company_id,
                "status_code": e.response.status_code,
            },
            exc_info=True,
        )
        raise self.retry(exc=e)
    except Exception as e:
        logger.error(
            f"Failed scrape_investor_relations task: {e}",
            extra={"task_id": task_id, "company_id": company_id},
            exc_info=True,
        )
        # Retry on transient errors
        if isinstance(e, (httpx.HTTPError, httpx.TimeoutException, ConnectionError)):
            raise self.retry(exc=e)
        raise


@celery_app.task(
    bind=True,
    name="app.tasks.scraping_tasks.download_pdf",
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(httpx.HTTPError, httpx.TimeoutException, ConnectionError, FileNotFoundError),
)
def download_pdf(self: Task, document_id: int) -> dict[str, Any]:
    """Download PDF document from URL and store locally.

    Args:
        document_id: ID of the document to download.

    Returns:
        Dictionary with task results including file path and hash.

    Raises:
        ValueError: If document not found or download fails.
    """
    task_id = self.request.id
    logger.info(
        "Starting download_pdf task",
        extra={"task_id": task_id, "document_id": document_id},
    )

    try:
        # Create progress callback for worker
        progress_callback = CeleryProgressCallback(self)

        # Create worker with database session
        async def _execute_worker():
            async with get_db_context() as session:
                worker = ScrapingWorker(session, progress_callback)
                return await worker.download_pdf(document_id)

        result = run_async(_execute_worker())

        # Add task_id to result for consistency
        result["task_id"] = task_id

        validate_task_result(result, ["task_id", "document_id", "status", "file_path"])
        logger.info(
            "Completed download_pdf task",
            extra={"task_id": task_id, "result": result},
        )

        return result

    except Exception as e:
        logger.error(
            f"Failed download_pdf task: {e}",
            extra={"task_id": task_id, "document_id": document_id},
            exc_info=True,
        )
        # Retry on transient errors
        if isinstance(e, (httpx.HTTPError, httpx.TimeoutException, ConnectionError)):
            raise self.retry(exc=e)
        raise


@celery_app.task(
    bind=True,
    name="app.tasks.scraping_tasks.classify_document",
    max_retries=2,
    default_retry_delay=30,
)
def classify_document(self: Task, document_id: int) -> dict[str, Any]:
    """Classify a document by type (annual_report, quarterly_report, etc.).

    Uses filename patterns, metadata, and content sampling to determine document type.

    Args:
        document_id: ID of the document to classify.

    Returns:
        Dictionary with task results including document type.

    Raises:
        ValueError: If document not found or classification fails.
    """
    task_id = self.request.id
    logger.info(
        "Starting classify_document task",
        extra={"task_id": task_id, "document_id": document_id},
    )

    try:
        # Create progress callback for worker
        progress_callback = CeleryProgressCallback(self)

        # Create worker with database session
        async def _execute_worker():
            async with get_db_context() as session:
                worker = ScrapingWorker(session, progress_callback)
                return await worker.classify_document(document_id)

        result = run_async(_execute_worker())

        # Add task_id to result for consistency
        result["task_id"] = task_id

        validate_task_result(result, ["task_id", "document_id", "status", "document_type"])
        logger.info(
            "Completed classify_document task",
            extra={"task_id": task_id, "result": result},
        )

        return result

    except Exception as e:
        logger.error(
            f"Failed classify_document task: {e}",
            extra={"task_id": task_id, "document_id": document_id},
            exc_info=True,
        )
        raise
