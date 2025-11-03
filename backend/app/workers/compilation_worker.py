"""
Worker for financial statement normalization and compilation.

Extracts business logic from compilation tasks for testability.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.compilation.compiler import StatementCompiler
from app.core.compilation.restatement import RestatementHandler
from app.core.normalization.normalizer import LineItemNormalizer
from app.db.models.extraction import CompiledStatement
from app.db.repositories.compiled_statement import CompiledStatementRepository
from app.db.repositories.document import DocumentRepository
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
        self.document_repo = DocumentRepository(session)
        self.compiled_statement_repo = CompiledStatementRepository(session)
        self.normalizer = LineItemNormalizer()
        self.compiler = StatementCompiler()
        self.restatement_handler = RestatementHandler()

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
        normalized_map = self.normalizer.normalize_line_items(extractions)

        self.update_progress("prioritizing_restated_data")

        # Map normalized names back to extractions for restatement handler
        # The restatement handler works with original names, so we need to preserve mapping
        extraction_with_normalized = []
        for extraction in extractions:
            # Create mapping of original -> normalized names
            raw_data = extraction.get("raw_data", {})
            line_items = raw_data.get("line_items", [])
            name_mapping = {}
            for item in line_items:
                original_name = item.get("item_name", "") or item.get("name", "")
                if original_name:
                    # Find normalized name
                    for canonical, entry in normalized_map.items():
                        variations = entry.get("variations", [])
                        for var in variations:
                            if var.get("original_name") == original_name:
                                name_mapping[original_name] = canonical
                                break

            extraction_copy = extraction.copy()
            extraction_copy["_normalized_names"] = name_mapping
            extraction_with_normalized.append(extraction_copy)

        # Prioritize restated data (newer reports override older)
        prioritized_data = self.restatement_handler.prioritize_restated_data(
            extraction_with_normalized
        )

        # Remap prioritized data to use normalized names
        prioritized_normalized = {}
        for year, line_items_year in prioritized_data.items():
            prioritized_normalized[year] = {}
            for original_name, value_data in line_items_year.items():
                # Find normalized name for this original
                normalized_name = original_name  # Default
                for extraction in extraction_with_normalized:
                    name_mapping = extraction.get("_normalized_names", {})
                    if original_name in name_mapping:
                        normalized_name = name_mapping[original_name]
                        break
                prioritized_normalized[year][normalized_name] = value_data

        self.update_progress("compiling_statement")

        # Get currency and unit from first extraction (assuming consistent)
        currency = "EUR"
        unit = "thousands"
        if extractions:
            raw_data = extractions[0].get("raw_data", {})
            currency = raw_data.get("currency", currency)
            unit = raw_data.get("unit", unit)

        # Compile multi-year statement
        compiled_data = self.compiler.compile_statement(
            normalized_map=normalized_map,
            prioritized_data=prioritized_normalized,
            statement_type=statement_type,
            currency=currency,
            unit=unit,
        )

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
            "compiled_statement_id": compiled_statement.id if compiled_statement else None,
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
        """Get all extractions for a company and statement type with document info."""
        from app.db.models.document import Document
        from app.db.models.extraction import Extraction

        # Use SQLAlchemy join to filter by company_id and get document info
        stmt = (
            select(Extraction, Document.fiscal_year)
            .join(Document, Extraction.document_id == Document.id)
            .where(
                Document.company_id == company_id,
                Extraction.statement_type == statement_type,
            )
            .order_by(Document.fiscal_year.desc())
        )
        result = await self.session.execute(stmt)
        rows = result.all()

        # Build extraction dicts with fiscal_year
        extractions = []
        for extraction, fiscal_year in rows:
            ext_dict = await self.extraction_repo._model_to_dict(extraction)
            ext_dict["fiscal_year"] = fiscal_year
            # Also add to raw_data for compatibility
            if "fiscal_year" not in ext_dict.get("raw_data", {}):
                ext_dict.setdefault("raw_data", {})["fiscal_year"] = fiscal_year
            extractions.append(ext_dict)

        return extractions


    async def _store_compiled_statement(
        self, company_id: int, statement_type: str, compiled_data: dict[str, Any]
    ) -> CompiledStatement:
        """Store compiled statement in database.

        Returns:
            CompiledStatement model instance.
        """
        return await self.compiled_statement_repo.upsert(
            company_id=company_id,
            statement_type=statement_type,
            data=compiled_data,
        )
