"""
Celery tasks for financial statement extraction from PDFs.

Tasks are thin wrappers around worker classes that handle business logic.
This separation allows testing business logic without Celery infrastructure.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

import logging
from typing import Any

from celery import Task

from app.core.storage import StorageServiceConfig, create_storage_service
from app.tasks.celery_app import celery_app
from app.tasks.progress import CeleryProgressCallback
from app.tasks.utils import get_db_context, run_async, validate_task_result
from app.workers.extraction_worker import ExtractionWorker
from config import Settings

logger = logging.getLogger(__name__)


def create_storage_service_from_config() -> Any:
    """Create storage service instance from application settings."""
    settings = Settings()
    config = StorageServiceConfig(
        enabled=settings.minio_enabled,
        endpoint=settings.minio_endpoint,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        bucket_name=settings.minio_bucket_name,
        use_ssl=settings.minio_use_ssl,
    )
    return create_storage_service(config)


@celery_app.task(
    bind=True,
    name="app.tasks.extraction_tasks.extract_financial_statements",
    max_retries=3,
    default_retry_delay=120,
    autoretry_for=(ConnectionError, TimeoutError),
    time_limit=1800,  # 30 minutes for LLM extraction
    soft_time_limit=1650,  # 27.5 minutes soft limit
)
def extract_financial_statements(self: Task, document_id: int) -> dict[str, Any]:
    """Extract financial statements from a PDF document using LLM.

    Args:
        document_id: ID of the document to extract from.

    Returns:
        Dictionary with task results including extracted statements.

    Raises:
        ValueError: If document not found or extraction fails.
    """
    task_id = self.request.id
    logger.info(
        "Starting extract_financial_statements task",
        extra={"task_id": task_id, "document_id": document_id},
    )

    try:
        # Create progress callback for worker
        progress_callback = CeleryProgressCallback(self)

        # Get OpenRouter settings
        settings = Settings()

        # Create worker with database session
        async def _execute_worker():
            async with get_db_context() as session:
                storage_service = create_storage_service_from_config()
                worker = ExtractionWorker(
                    session,
                    openrouter_api_key=settings.open_router_api_key,
                    openrouter_model=settings.open_router_model_extraction,
                    progress_callback=progress_callback,
                    storage_service=storage_service,
                )
                return await worker.extract_financial_statements(document_id)

        result = run_async(_execute_worker())

        # Add task_id to result for consistency
        result["task_id"] = task_id

        validate_task_result(result, ["task_id", "document_id", "status", "extracted_statements"])
        logger.info(
            "Completed extract_financial_statements task",
            extra={"task_id": task_id, "result": result},
        )

        return result

    except Exception as e:
        logger.error(
            f"Failed extract_financial_statements task: {e}",
            extra={"task_id": task_id, "document_id": document_id},
            exc_info=True,
        )
        # Retry on transient errors
        if isinstance(e, (ConnectionError, TimeoutError)):
            raise self.retry(exc=e) from e
        raise


@celery_app.task(
    bind=True,
    name="app.tasks.extraction_tasks.process_document",
    max_retries=2,
    default_retry_delay=60,
)
def process_document(self: Task, document_id: int) -> dict[str, Any]:
    """Process a document end-to-end: classify, download, and extract.

    This is a convenience task that orchestrates multiple steps.

    Args:
        document_id: ID of the document to process.

    Returns:
        Dictionary with task results from all processing steps.
    """
    task_id = self.request.id
    logger.info(
        "Starting process_document task",
        extra={"task_id": task_id, "document_id": document_id},
    )

    try:
        # Create progress callback for worker
        progress_callback = CeleryProgressCallback(self)

        # Get OpenRouter settings
        settings = Settings()

        # Create worker with database session
        async def _execute_worker():
            async with get_db_context() as session:
                storage_service = create_storage_service_from_config()
                worker = ExtractionWorker(
                    session,
                    openrouter_api_key=settings.open_router_api_key,
                    openrouter_model=settings.open_router_model_extraction,
                    progress_callback=progress_callback,
                    storage_service=storage_service,
                )
                return await worker.process_document(document_id)

        result = run_async(_execute_worker())

        # Add task_id to result for consistency
        result["task_id"] = task_id

        validate_task_result(result, ["task_id", "document_id", "status"])
        logger.info(
            "Completed process_document task",
            extra={"task_id": task_id, "result": result},
        )

        return result

    except Exception as e:
        logger.error(
            f"Failed process_document task: {e}",
            extra={"task_id": task_id, "document_id": document_id},
            exc_info=True,
        )
        raise
