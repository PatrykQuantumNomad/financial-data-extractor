"""
Celery tasks for financial statement normalization and compilation.

Tasks handle normalizing line items across years, deduplication,
and compiling multi-year statements.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

import logging
from typing import Any

from celery import Task

from app.db.repositories.compiled_statement import CompiledStatementRepository
from app.db.repositories.extraction import ExtractionRepository
from app.tasks.celery_app import celery_app
from app.tasks.utils import get_db_context, run_async, validate_task_result

logger = logging.getLogger(__name__)


@celery_app.task(
    bind=True,
    name="app.tasks.compilation_tasks.normalize_and_compile_statements",
    max_retries=2,
    default_retry_delay=60,
    time_limit=1800,  # 30 minutes for compilation
    soft_time_limit=1650,  # 27.5 minutes soft limit
)
def normalize_and_compile_statements(self: Task, company_id: int, statement_type: str) -> dict[str, Any]:
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
        f"Starting normalize_and_compile_statements task",
        extra={"task_id": task_id, "company_id": company_id, "statement_type": statement_type},
    )

    try:
        # Update task state
        self.update_state(state="PROGRESS", meta={"step": "fetching_extractions"})

        # Get all extractions for company and statement type
        extractions = run_async(_get_extractions_for_company(company_id, statement_type))

        if not extractions:
            logger.warning(
                f"No extractions found for company {company_id} and statement type {statement_type}",
                extra={"task_id": task_id, "company_id": company_id, "statement_type": statement_type},
            )
            return {
                "task_id": task_id,
                "company_id": company_id,
                "statement_type": statement_type,
                "status": "success",
                "message": "no_extractions_found",
                "compiled_data": {},
            }

        logger.info(
            f"Found {len(extractions)} extractions",
            extra={"task_id": task_id, "company_id": company_id, "statement_type": statement_type, "count": len(extractions)},
        )

        # Update task state
        self.update_state(state="PROGRESS", meta={"step": "normalizing_line_items"})

        # Normalize line items across extractions
        normalized_data = run_async(_normalize_line_items(extractions))

        # Update task state
        self.update_state(state="PROGRESS", meta={"step": "compiling_statement"})

        # Compile multi-year statement
        compiled_data = run_async(_compile_multi_year_statement(normalized_data, extractions))

        # Update task state
        self.update_state(state="PROGRESS", meta={"step": "storing_compiled_statement"})

        # Store compiled statement in database
        compiled_statement = run_async(_store_compiled_statement(company_id, statement_type, compiled_data))

        result = {
            "task_id": task_id,
            "company_id": company_id,
            "statement_type": statement_type,
            "status": "success",
            "extraction_count": len(extractions),
            "line_item_count": len(compiled_data.get("line_items", [])),
            "years": compiled_data.get("years", []),
            "compiled_statement_id": compiled_statement.get("id") if compiled_statement else None,
        }

        validate_task_result(result, ["task_id", "company_id", "statement_type", "status"])
        logger.info(f"Completed normalize_and_compile_statements task", extra={"task_id": task_id, "result": result})

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
    logger.info(f"Starting compile_company_statements task", extra={"task_id": task_id, "company_id": company_id})

    try:
        statement_types = ["income_statement", "balance_sheet", "cash_flow_statement"]
        results = {}

        for stmt_type in statement_types:
            self.update_state(
                state="PROGRESS",
                meta={"step": f"compiling_{stmt_type}", "current": statement_types.index(stmt_type) + 1, "total": len(statement_types)},
            )

            result = normalize_and_compile_statements.apply(args=[company_id, stmt_type]).get()
            results[stmt_type] = result

        overall_result = {
            "task_id": task_id,
            "company_id": company_id,
            "status": "success",
            "statements": results,
        }

        validate_task_result(overall_result, ["task_id", "company_id", "status"])
        logger.info(f"Completed compile_company_statements task", extra={"task_id": task_id, "result": overall_result})

        return overall_result

    except Exception as e:
        logger.error(
            f"Failed compile_company_statements task: {e}",
            extra={"task_id": task_id, "company_id": company_id},
            exc_info=True,
        )
        raise


# Helper functions (async)

async def _get_extractions_for_company(company_id: int, statement_type: str) -> list[dict[str, Any]]:
    """Get all extractions for a company and statement type."""
    async with get_db_context() as pool:
        extraction_repo = ExtractionRepository(pool)
        # Need to join with documents to filter by company_id
        query = """
            SELECT e.*
            FROM extractions e
            INNER JOIN documents d ON e.document_id = d.id
            WHERE d.company_id = %(company_id)s
            AND e.statement_type = %(statement_type)s
            ORDER BY d.fiscal_year DESC
        """
        params = {"company_id": company_id, "statement_type": statement_type}
        return await extraction_repo.execute_query(query, params)


async def _normalize_line_items(extractions: list[dict[str, Any]]) -> dict[str, Any]:
    """Normalize line item names across extractions using fuzzy matching.

    TODO: Implement actual normalization logic using rapidfuzz.
    Should:
    - Group similar line item names
    - Apply manual mappings
    - Handle variations (Revenue vs Revenues vs Total Revenue)

    Args:
        extractions: List of extraction records.

    Returns:
        Dictionary mapping normalized names to original variations.
    """
    from rapidfuzz import fuzz

    # Collect all unique line item names
    line_items_map = {}
    for extraction in extractions:
        raw_data = extraction.get("raw_data", {})
        line_items = raw_data.get("line_items", [])

        for item in line_items:
            item_name = item.get("name", "")
            if not item_name:
                continue

            # Check for similar names using fuzzy matching
            normalized_name = None
            threshold = 85  # Similarity threshold

            for existing_name in line_items_map.keys():
                similarity = fuzz.ratio(item_name.lower(), existing_name.lower())
                if similarity >= threshold:
                    normalized_name = existing_name
                    break

            if not normalized_name:
                normalized_name = item_name

            if normalized_name not in line_items_map:
                line_items_map[normalized_name] = []

            line_items_map[normalized_name].append({
                "original": item_name,
                "extraction_id": extraction.get("id"),
                "document_id": extraction.get("document_id"),
            })

    return {"normalized_map": line_items_map}


async def _compile_multi_year_statement(
    normalized_data: dict[str, Any], extractions: list[dict[str, Any]]
) -> dict[str, Any]:
    """Compile multi-year statement from normalized data.

    Args:
        normalized_data: Normalized line item mapping.
        extractions: List of extraction records with fiscal year info.

    Returns:
        Compiled statement data with all years and line items.
    """
    # Get all years from extractions (need to join with documents)
    async with get_db_context() as pool:
        extraction_repo = ExtractionRepository(pool)

        # Get unique years by querying documents directly
        # Since we already have extraction IDs, we can join with documents
        # Use array parameter for psycopg3
        extraction_ids = [ext["id"] for ext in extractions]
        if not extraction_ids:
            years = []
        else:
            query = """
                SELECT DISTINCT d.fiscal_year
                FROM documents d
                INNER JOIN extractions e ON e.document_id = d.id
                WHERE e.id = ANY(%(extraction_ids)s)
                ORDER BY d.fiscal_year DESC
            """
            years_result = await extraction_repo.execute_query(query, {"extraction_ids": extraction_ids})
            years = [row["fiscal_year"] for row in years_result] if years_result else []

    # Build compiled statement structure
    compiled_line_items = []
    normalized_map = normalized_data.get("normalized_map", {})

    for normalized_name, variations in normalized_map.items():
        line_item = {"name": normalized_name}
        # Get values for each year
        for year in years:
            # Find extraction with this year and get value
            # This is simplified - actual implementation should handle restatements
            value = _get_value_for_year(variations, year, extractions)
            line_item[str(year)] = value

        compiled_line_items.append(line_item)

    return {
        "line_items": compiled_line_items,
        "years": years,
        "metadata": {
            "extraction_count": len(extractions),
            "normalized_line_item_count": len(normalized_map),
        },
    }


def _get_value_for_year(
    variations: list[dict[str, Any]], year: int, extractions: list[dict[str, Any]]
) -> Any | None:
    """Get value for a specific year from variations.

    TODO: Implement logic to:
    - Find extraction for the year
    - Prioritize restated data from newer reports
    - Handle missing values

    Args:
        variations: List of variations for the line item.
        year: Fiscal year to get value for.
        extractions: List of extraction records.

    Returns:
        Value for the year, or None if not found.
    """
    # Simplified implementation
    # Should prioritize restated data from newer reports
    for variation in variations:
        extraction_id = variation.get("extraction_id")
        extraction = next((e for e in extractions if e.get("id") == extraction_id), None)
        if extraction:
            # Get fiscal year from document (would need join)
            # For now, return None - needs proper implementation
            pass

    return None


async def _store_compiled_statement(
    company_id: int, statement_type: str, compiled_data: dict[str, Any]
) -> dict[str, Any]:
    """Store compiled statement in database."""
    async with get_db_context() as pool:
        repo = CompiledStatementRepository(pool)
        return await repo.upsert(
            company_id=company_id,
            statement_type=statement_type,
            data=compiled_data,
        )
