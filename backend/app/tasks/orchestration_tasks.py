"""
Celery tasks for orchestrating end-to-end workflows.

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
from app.workers.orchestration_worker import OrchestrationWorker
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
    name="app.tasks.orchestration_tasks.extract_company_financial_data",
    max_retries=2,
    default_retry_delay=300,
    time_limit=7200,  # 2 hours for full extraction
    soft_time_limit=6900,  # 1h 55min soft limit
)
def extract_company_financial_data(self: Task, company_id: int) -> dict[str, Any]:
    """Orchestrate complete financial data extraction for a company.

    This is the main entry point for extracting 10 years of financial data:
    1. Scrape investor relations website
    2. Discover and classify documents
    3. Download PDFs
    4. Extract financial statements
    5. Normalize and compile statements

    Args:
        company_id: ID of the company to extract data for.

    Returns:
        Dictionary with task results from all steps.

    Raises:
        ValueError: If company not found or extraction fails.
    """
    task_id = self.request.id
    logger.info(
        "Starting extract_company_financial_data task",
        extra={"task_id": task_id, "company_id": company_id},
    )

    try:
        # Create progress callback for worker
        progress_callback = CeleryProgressCallback(self)

        # Create worker with database session
        async def _execute_worker():
            async with get_db_context() as session:
                storage_service = create_storage_service_from_config()
                worker = OrchestrationWorker(session, progress_callback=progress_callback, storage_service=storage_service)
                return await worker.extract_company_financial_data(company_id)

        result = run_async(_execute_worker())

        # Add task_id to result for consistency
        result["task_id"] = task_id

        validate_task_result(result, ["task_id", "company_id", "status"])
        logger.info(
            "Completed extract_company_financial_data task",
            extra={"task_id": task_id, "company_id": company_id, "result": result},
        )

        return result

    except Exception as e:
        logger.error(
            f"Failed extract_company_financial_data task: {e}",
            extra={"task_id": task_id, "company_id": company_id},
            exc_info=True,
        )
        raise


@celery_app.task(
    bind=True,
    name="app.tasks.orchestration_tasks.process_all_documents",
    max_retries=2,
    default_retry_delay=300,
    time_limit=7200,  # 2 hours for batch processing
    soft_time_limit=6900,  # 1h 55min soft limit
)
def process_all_documents(self: Task, company_id: int) -> dict[str, Any]:
    """Process all documents for a company through classify, download, and extract.

    Args:
        company_id: ID of the company.

    Returns:
        Dictionary with processing results for all documents.
    """
    task_id = self.request.id
    logger.info(
        "Starting process_all_documents task",
        extra={"task_id": task_id, "company_id": company_id},
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
                extraction_worker = ExtractionWorker(
                    session,
                    openrouter_api_key=settings.open_router_api_key,
                    openrouter_model=settings.open_router_model_extraction,
                    progress_callback=progress_callback,
                    storage_service=storage_service,
                )
                worker = OrchestrationWorker(
                    session,
                    extraction_worker=extraction_worker,
                    progress_callback=progress_callback,
                    storage_service=storage_service,
                )
                return await worker.process_all_documents(company_id)

        result = run_async(_execute_worker())

        # Add task_id to result for consistency
        result["task_id"] = task_id

        validate_task_result(result, ["task_id", "company_id", "status"])
        logger.info(
            "Completed process_all_documents task",
            extra={"task_id": task_id, "company_id": company_id, "result": result},
        )

        return result

    except Exception as e:
        logger.error(
            f"Failed process_all_documents task: {e}",
            extra={"task_id": task_id, "company_id": company_id},
            exc_info=True,
        )
        raise


@celery_app.task(
    bind=True,
    name="app.tasks.orchestration_tasks.recompile_company_statements",
    max_retries=2,
    default_retry_delay=60,
)
def recompile_company_statements(self: Task, company_id: int) -> dict[str, Any]:
    """Recompile all statements for a company after new extractions.

    Useful when new documents are processed and statements need to be updated.

    Args:
        company_id: ID of the company.

    Returns:
        Dictionary with compilation results.
    """
    task_id = self.request.id
    logger.info(
        "Starting recompile_company_statements task",
        extra={"task_id": task_id, "company_id": company_id},
    )

    try:
        # Create progress callback for worker
        progress_callback = CeleryProgressCallback(self)

        # Create worker with database session
        async def _execute_worker():
            async with get_db_context() as session:
                storage_service = create_storage_service_from_config()
                worker = OrchestrationWorker(session, progress_callback=progress_callback, storage_service=storage_service)
                return await worker.recompile_company_statements(company_id)

        overall_result = run_async(_execute_worker())

        # Add task_id to result for consistency
        overall_result["task_id"] = task_id

        validate_task_result(overall_result, ["task_id", "company_id", "status"])
        logger.info(
            "Completed recompile_company_statements task",
            extra={"task_id": task_id, "company_id": company_id, "result": overall_result},
        )

        return overall_result

    except Exception as e:
        logger.error(
            f"Failed recompile_company_statements task: {e}",
            extra={"task_id": task_id, "company_id": company_id},
            exc_info=True,
        )
        raise
