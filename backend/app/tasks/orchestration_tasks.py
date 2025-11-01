"""
Celery tasks for orchestrating end-to-end workflows.

High-level tasks that coordinate multiple processing steps.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

import logging
from typing import Any

from celery import Task, group

from app.tasks.celery_app import celery_app
from app.tasks.compilation_tasks import compile_company_statements
from app.tasks.extraction_tasks import process_document
from app.tasks.scraping_tasks import scrape_investor_relations
from app.tasks.utils import get_db_context, run_async, validate_task_result

logger = logging.getLogger(__name__)


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
        f"Starting extract_company_financial_data task",
        extra={"task_id": task_id, "company_id": company_id},
    )

    try:
        # Verify company exists
        company_data = run_async(_get_company_info(company_id))
        if not company_data:
            raise ValueError(f"Company with id {company_id} not found")

        # Step 1: Scrape investor relations website
        self.update_state(state="PROGRESS", meta={"step": "scraping", "progress": 10})

        scrape_result = scrape_investor_relations.apply(args=[company_id]).get()
        discovered_documents = scrape_result.get("documents", [])

        logger.info(
            f"Scraping completed, found {len(discovered_documents)} documents",
            extra={"task_id": task_id, "company_id": company_id, "document_count": len(discovered_documents)},
        )

        # Step 2: Process all documents (classify, download, extract)
        self.update_state(state="PROGRESS", meta={"step": "processing_documents", "progress": 30})

        document_ids = [doc["id"] for doc in discovered_documents]
        processing_results = []

        # Process documents in batches to avoid overwhelming workers
        batch_size = 5
        for i in range(0, len(document_ids), batch_size):
            batch = document_ids[i : i + batch_size]
            self.update_state(
                state="PROGRESS",
                meta={
                    "step": "processing_documents",
                    "progress": 30 + int((i / len(document_ids)) * 50),
                    "processed": i,
                    "total": len(document_ids),
                },
            )

            # Create group of processing tasks
            processing_group = group(
                process_document.s(document_id) for document_id in batch
            )
            batch_results = processing_group.apply_async().get()

            processing_results.extend(batch_results)

            logger.info(
                f"Processed batch {i // batch_size + 1}",
                extra={"task_id": task_id, "company_id": company_id, "batch_size": len(batch)},
            )

        # Step 3: Compile statements
        self.update_state(state="PROGRESS", meta={"step": "compiling_statements", "progress": 85})

        compilation_result = compile_company_statements.apply(args=[company_id]).get()

        # Step 4: Summary
        successful_documents = [r for r in processing_results if r.get("status") == "success"]
        failed_documents = [r for r in processing_results if r.get("status") != "success"]

        result = {
            "task_id": task_id,
            "company_id": company_id,
            "status": "success",
            "summary": {
                "discovered_documents": len(discovered_documents),
                "processed_documents": len(processing_results),
                "successful_documents": len(successful_documents),
                "failed_documents": len(failed_documents),
            },
            "steps": {
                "scraping": scrape_result,
                "processing": processing_results,
                "compilation": compilation_result,
            },
        }

        validate_task_result(result, ["task_id", "company_id", "status", "summary"])
        logger.info(
            f"Completed extract_company_financial_data task",
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
        f"Starting recompile_company_statements task",
        extra={"task_id": task_id, "company_id": company_id},
    )

    try:
        result = compile_company_statements.apply(args=[company_id]).get()

        overall_result = {
            "task_id": task_id,
            "company_id": company_id,
            "status": "success",
            "compilation": result,
        }

        validate_task_result(overall_result, ["task_id", "company_id", "status"])
        logger.info(
            f"Completed recompile_company_statements task",
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


# Helper functions (async)

async def _get_company_info(company_id: int) -> dict[str, Any] | None:
    """Get company information from database."""
    from app.db.repositories.company import CompanyRepository

    async with get_db_context() as pool:
        repo = CompanyRepository(pool)
        return await repo.get_by_id(company_id)
