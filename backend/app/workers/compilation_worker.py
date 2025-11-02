"""
Worker for financial statement normalization and compilation.

Extracts business logic from compilation tasks for testability.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

import logging
from typing import Any

from sqlalchemy import distinct, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.compiled_statement import CompiledStatementRepository
from app.db.repositories.extraction import ExtractionRepository
from app.workers.base import BaseWorker

logger = logging.getLogger(__name__)


class CompilationWorker(BaseWorker):
    """Worker for normalizing and compiling financial statements.

    Handles:
    - Normalizing line items across years
    - Deduplication and fuzzy matching
    - Compiling multi-year statements
    """

    def __init__(
        self,
        session: AsyncSession,
        progress_callback: Any | None = None,
    ):
        """Initialize compilation worker.

        Args:
            session: Database async session.
            progress_callback: Optional callback for progress updates.
        """
        super().__init__(progress_callback)
        self.session = session
        self.extraction_repo = ExtractionRepository(session)
        self.compiled_statement_repo = CompiledStatementRepository(session)

    async def normalize_and_compile_statements(
        self, company_id: int, statement_type: str
    ) -> dict[str, Any]:
        """Normalize and compile financial statements for a company and statement type.

        Args:
            company_id: ID of the company.
            statement_type: Type of statement (income_statement, balance_sheet, cash_flow_statement).

        Returns:
            Dictionary with task results including compiled statement data.
        """
        self.logger.info(
            "Starting normalize_and_compile_statements",
            extra={"company_id": company_id, "statement_type": statement_type},
        )

        self.update_progress("fetching_extractions")

        # Get all extractions for company and statement type
        extractions = await self._get_extractions_for_company(company_id, statement_type)

        if not extractions:
            self.logger.warning(
                f"No extractions found for company {company_id} and statement type {statement_type}",
                extra={"company_id": company_id, "statement_type": statement_type},
            )
            return {
                "company_id": company_id,
                "statement_type": statement_type,
                "status": "success",
                "message": "no_extractions_found",
                "compiled_data": {},
            }

        self.logger.info(
            f"Found {len(extractions)} extractions",
            extra={
                "company_id": company_id,
                "statement_type": statement_type,
                "count": len(extractions),
            },
        )

        self.update_progress("normalizing_line_items")

        # Normalize line items across extractions
        normalized_data = await self._normalize_line_items(extractions)

        self.update_progress("compiling_statement")

        # Compile multi-year statement
        compiled_data = await self._compile_multi_year_statement(normalized_data, extractions)

        self.update_progress("storing_compiled_statement")

        # Store compiled statement in database
        compiled_statement = await self._store_compiled_statement(
            company_id, statement_type, compiled_data
        )

        result = {
            "company_id": company_id,
            "statement_type": statement_type,
            "status": "success",
            "extraction_count": len(extractions),
            "line_item_count": len(compiled_data.get("line_items", [])),
            "years": compiled_data.get("years", []),
            "compiled_statement_id": compiled_statement.get("id") if compiled_statement else None,
        }

        self.logger.info(
            "Completed normalize_and_compile_statements",
            extra={"company_id": company_id, "statement_type": statement_type, "result": result},
        )

        return result

    async def compile_company_statements(self, company_id: int) -> dict[str, Any]:
        """Compile all statement types for a company.

        Args:
            company_id: ID of the company.

        Returns:
            Dictionary with task results for all statement types.
        """
        self.logger.info(
            "Starting compile_company_statements",
            extra={"company_id": company_id},
        )

        statement_types = ["income_statement", "balance_sheet", "cash_flow_statement"]
        results = {}

        for i, stmt_type in enumerate(statement_types):
            self.update_progress(
                f"compiling_{stmt_type}",
                {
                    "current": i + 1,
                    "total": len(statement_types),
                    "statement_type": stmt_type,
                },
            )

            result = await self.normalize_and_compile_statements(company_id, stmt_type)
            results[stmt_type] = result

        overall_result = {
            "company_id": company_id,
            "status": "success",
            "statements": results,
        }

        self.logger.info(
            "Completed compile_company_statements",
            extra={"company_id": company_id, "result": overall_result},
        )

        return overall_result

    async def execute(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        """Execute worker operation (required by BaseWorker).

        This worker has specific methods, so execute is not used directly.
        """
        raise NotImplementedError(
            "CompilationWorker uses specific methods (normalize_and_compile_statements, "
            "compile_company_statements) instead of execute"
        )

    # Helper methods

    async def _get_extractions_for_company(
        self, company_id: int, statement_type: str
    ) -> list[dict[str, Any]]:
        """Get all extractions for a company and statement type."""
        from app.db.models.document import Document
        from app.db.models.extraction import Extraction

        # Use SQLAlchemy join to filter by company_id
        stmt = (
            select(Extraction)
            .join(Document, Extraction.document_id == Document.id)
            .where(
                Document.company_id == company_id,
                Extraction.statement_type == statement_type,
            )
            .order_by(Document.fiscal_year.desc())
        )
        result = await self.session.execute(stmt)
        extractions = result.scalars().all()
        return [await self.extraction_repo._model_to_dict(ext) for ext in extractions]

    async def _normalize_line_items(self, extractions: list[dict[str, Any]]) -> dict[str, Any]:
        """Normalize line item names across extractions using fuzzy matching.

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

                line_items_map[normalized_name].append(
                    {
                        "original": item_name,
                        "extraction_id": extraction.get("id"),
                        "document_id": extraction.get("document_id"),
                    }
                )

        return {"normalized_map": line_items_map}

    async def _compile_multi_year_statement(
        self, normalized_data: dict[str, Any], extractions: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Compile multi-year statement from normalized data.

        Args:
            normalized_data: Normalized line item mapping.
            extractions: List of extraction records with fiscal year info.

        Returns:
            Compiled statement data with all years and line items.
        """
        from app.db.models.document import Document
        from app.db.models.extraction import Extraction

        # Get unique years by querying documents directly
        extraction_ids = [ext["id"] for ext in extractions]
        if not extraction_ids:
            years = []
        else:
            # Get distinct fiscal years using ORM join
            stmt = (
                select(distinct(Document.fiscal_year))
                .join(Extraction, Document.id == Extraction.document_id)
                .where(Extraction.id.in_(extraction_ids))
                .order_by(Document.fiscal_year.desc())
            )
            result = await self.session.execute(stmt)
            years = [row[0] for row in result.all()]

        # Build compiled statement structure
        compiled_line_items = []
        normalized_map = normalized_data.get("normalized_map", {})

        for normalized_name, variations in normalized_map.items():
            line_item = {"name": normalized_name}
            # Get values for each year
            for year in years:
                # Find extraction with this year and get value
                # This is simplified - actual implementation should handle restatements
                value = await self._get_value_for_year(variations, year, extractions)
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

    async def _get_value_for_year(
        self,
        variations: list[dict[str, Any]],
        year: int,
        extractions: list[dict[str, Any]],
    ) -> Any | None:
        """Get value for a specific year from variations.

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
                document_id = extraction.get("document_id")
                # Get document to check fiscal year
                # This is a simplified version - real implementation would
                # need to join with documents to get fiscal_year
                # and match against the requested year
                pass

        return None

    async def _store_compiled_statement(
        self, company_id: int, statement_type: str, compiled_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Store compiled statement in database."""
        return await self.compiled_statement_repo.upsert(
            company_id=company_id,
            statement_type=statement_type,
            data=compiled_data,
        )
