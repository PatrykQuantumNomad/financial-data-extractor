"""
Worker for orchestrating end-to-end workflows.

Extracts business logic from orchestration tasks for testability.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.storage import IStorageService
from app.db.repositories.company import CompanyRepository
from app.workers.base import BaseWorker
from app.workers.compilation_worker import CompilationWorker
from app.workers.scraping_worker import ScrapingWorker

logger = logging.getLogger(__name__)


class OrchestrationWorker(BaseWorker):
    """Worker for orchestrating end-to-end financial data extraction workflows.

    Coordinates multiple workers to complete full extraction pipelines.
    """

    def __init__(
        self,
        session: AsyncSession,
        scraping_worker: ScrapingWorker | None = None,
        compilation_worker: CompilationWorker | None = None,
        progress_callback: Any | None = None,
        storage_service: IStorageService | None = None,
    ):
        """Initialize orchestration worker.

        Args:
            session: Database async session.
            scraping_worker: Optional ScrapingWorker instance (created if not provided).
            compilation_worker: Optional CompilationWorker instance (created if not provided).
            progress_callback: Optional callback for progress updates.
            storage_service: Optional storage service for PDF files.
        """
        super().__init__(progress_callback)
        self.session = session
        self.company_repo = CompanyRepository(session)
        self.scraping_worker = scraping_worker or ScrapingWorker(session, progress_callback, storage_service)
        self.compilation_worker = compilation_worker or CompilationWorker(
            session, progress_callback
        )

    async def extract_company_financial_data(self, company_id: int) -> dict[str, Any]:
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
            ValueError: If company not found.
        """
        self.logger.info(
            "Starting extract_company_financial_data",
            extra={"company_id": company_id},
        )

        # Verify company exists
        company_data = await self.company_repo.get_by_id(company_id)
        if not company_data:
            raise ValueError(f"Company with id {company_id} not found")

        # Step 1: Scrape investor relations website
        self.update_progress("scraping", {"progress": 10})

        from config import Settings

        settings = Settings()
        scrape_result = await self.scraping_worker.scrape_investor_relations(
            company_id, settings.open_router_api_key
        )
        discovered_documents = scrape_result.get("documents", [])

        self.logger.info(
            f"Scraping completed, found {len(discovered_documents)} documents",
            extra={"company_id": company_id, "document_count": len(discovered_documents)},
        )

        # Step 2: Process all documents (classify, download, extract)
        # Note: In a full implementation, this would coordinate with ExtractionWorker
        # For now, we'll just log that documents were discovered
        self.update_progress("processing_documents", {"progress": 30})

        # Step 3: Compile statements
        self.update_progress("compiling_statements", {"progress": 85})

        compilation_result = await self.compilation_worker.compile_company_statements(company_id)

        result = {
            "company_id": company_id,
            "status": "success",
            "summary": {
                "discovered_documents": len(discovered_documents),
            },
            "steps": {
                "scraping": scrape_result,
                "compilation": compilation_result,
            },
        }

        self.logger.info(
            "Completed extract_company_financial_data",
            extra={"company_id": company_id, "result": result},
        )

        return result

    async def recompile_company_statements(self, company_id: int) -> dict[str, Any]:
        """Recompile all statements for a company after new extractions.

        Args:
            company_id: ID of the company.

        Returns:
            Dictionary with compilation results.
        """
        self.logger.info(
            "Starting recompile_company_statements",
            extra={"company_id": company_id},
        )

        result = await self.compilation_worker.compile_company_statements(company_id)

        overall_result = {
            "company_id": company_id,
            "status": "success",
            "compilation": result,
        }

        self.logger.info(
            "Completed recompile_company_statements",
            extra={"company_id": company_id, "result": overall_result},
        )

        return overall_result

    async def execute(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        """Execute worker operation (required by BaseWorker).

        This worker has specific methods, so execute is not used directly.
        """
        raise NotImplementedError(
            "OrchestrationWorker uses specific methods (extract_company_financial_data, "
            "recompile_company_statements) instead of execute"
        )
