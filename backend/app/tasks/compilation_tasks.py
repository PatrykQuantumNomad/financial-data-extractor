"""
Celery tasks for financial statement normalization and compilation.

Tasks are thin wrappers around worker classes that handle business logic.
This separation allows testing business logic without Celery infrastructure.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

import logging
from typing import Any

from celery import Task

from app.tasks.celery_app import celery_app
from app.tasks.progress import CeleryProgressCallback
from app.tasks.utils import get_db_context, run_async, validate_task_result
from app.workers.compilation_worker import CompilationWorker

logger = logging.getLogger(__name__)


@celery_app.task(
    bind=True,
    name="app.tasks.compilation_tasks.normalize_and_compile_statements",
    max_retries=2,
    default_retry_delay=60,
    time_limit=1800,  # 30 minutes for compilation
    soft_time_limit=1650,  # 27.5 minutes soft limit
)
def normalize_and_compile_statements(
    self: Task, company_id: int, statement_type: str
) -> dict[str, Any]:
    """Normalize and compile financial statements for a company and statement type.

    Aggregates all extractions across years, normalizes line item names,
    and creates compiled statement.

    Args:
        company_id: ID of the company.
        statement_type: Type of statement (income_statement, balance_sheet, cash_flow_statement).

    Returns:
        Dictionary with task results including compiled statement data.

    Raises:
        ValueError: If company not found or compilation fails.
    """
    task_id = self.request.id
    logger.info(
        "Starting normalize_and_compile_statements task",
        extra={"task_id": task_id, "company_id": company_id, "statement_type": statement_type},
    )

    try:
        # Create progress callback for worker
        progress_callback = CeleryProgressCallback(self)

        # Create worker with database session
        async def _execute_worker():
            async with get_db_context() as session:
                worker = CompilationWorker(session, progress_callback)
                return await worker.normalize_and_compile_statements(company_id, statement_type)

        result = run_async(_execute_worker())

        # Add task_id to result for consistency
        result["task_id"] = task_id

        validate_task_result(result, ["task_id", "company_id", "statement_type", "status"])
        logger.info(
            "Completed normalize_and_compile_statements task",
            extra={"task_id": task_id, "result": result},
        )

        return result

    except Exception as e:
        logger.error(
            f"Failed normalize_and_compile_statements task: {e}",
            extra={"task_id": task_id, "company_id": company_id, "statement_type": statement_type},
            exc_info=True,
        )
        raise


@celery_app.task(
    bind=True,
    name="app.tasks.compilation_tasks.compile_company_statements",
    max_retries=2,
    default_retry_delay=60,
)
def compile_company_statements(self: Task, company_id: int) -> dict[str, Any]:
    """Compile all statement types for a company.

    Runs normalization and compilation for all three statement types:
    income_statement, balance_sheet, cash_flow_statement.

    Args:
        company_id: ID of the company.

    Returns:
        Dictionary with task results for all statement types.
    """
    task_id = self.request.id
    logger.info(
        "Starting compile_company_statements task",
        extra={"task_id": task_id, "company_id": company_id},
    )

    try:
        # Create progress callback for worker
        progress_callback = CeleryProgressCallback(self)

        # Create worker with database session
        async def _execute_worker():
            async with get_db_context() as session:
                worker = CompilationWorker(session, progress_callback)
                return await worker.compile_company_statements(company_id)

        overall_result = run_async(_execute_worker())

        # Add task_id to result for consistency
        overall_result["task_id"] = task_id

        validate_task_result(overall_result, ["task_id", "company_id", "status"])
        logger.info(
            "Completed compile_company_statements task",
            extra={"task_id": task_id, "result": overall_result},
        )

        return overall_result

    except Exception as e:
        logger.error(
            f"Failed compile_company_statements task: {e}",
            extra={"task_id": task_id, "company_id": company_id},
            exc_info=True,
        )
        raise
