"""
Worker for financial statement extraction from PDFs.

Extracts business logic from extraction tasks for testability.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.llm.client import OpenRouterClient
from app.core.llm.extractor import FinancialStatementExtractor
from app.core.pdf.extractor import PDFExtractor
from app.core.storage import IStorageService
from app.db.repositories.document import DocumentRepository
from app.db.repositories.extraction import ExtractionRepository
from app.workers.base import BaseWorker

logger = logging.getLogger(__name__)


class ExtractionWorker(BaseWorker):
    """Worker for extracting financial statements from PDF documents.

    Handles:
    - PDF processing and text extraction
    - LLM-based financial statement extraction
    - Storing extraction results
    """

    def __init__(
        self,
        session: AsyncSession,
        openrouter_api_key: str | None = None,
        progress_callback: Any | None = None,
        storage_service: IStorageService | None = None,
        openrouter_model: str | None = None,
    ):
        """Initialize extraction worker.

        Args:
            session: Database async session.
            openrouter_api_key: Optional OpenRouter API key (will be loaded from config if not provided).
            progress_callback: Optional callback for progress updates.
            storage_service: Optional storage service for PDF files.
            openrouter_model: Optional model to use via OpenRouter (defaults to open_router_model_extraction from config).
        """
        super().__init__(progress_callback)
        self.session = session
        self.document_repo = DocumentRepository(session)
        self.extraction_repo = ExtractionRepository(session)
        self.storage_service = storage_service

        # Initialize OpenRouter client
        from config import Settings

        settings = Settings()
        if not openrouter_api_key:
            openrouter_api_key = settings.open_router_api_key

        # Get model from config if not provided
        if openrouter_model is None:
            openrouter_model = settings.open_router_model_extraction

        self.openrouter_client = OpenRouterClient(
            api_key=openrouter_api_key,
            default_model=openrouter_model,
        )
        self.extractor = FinancialStatementExtractor(self.openrouter_client, model=openrouter_model)
        self.pdf_extractor = PDFExtractor()

    async def extract_financial_statements(self, document_id: int) -> dict[str, Any]:
        """Extract financial statements from a PDF document using LLM.

        Args:
            document_id: ID of the document to extract from.

        Returns:
            Dictionary with task results including extracted statements.

        Raises:
            ValueError: If document not found or extraction fails.
        """
        self.logger.info(
            "Starting extract_financial_statements",
            extra={"document_id": document_id},
        )

        self.update_progress("fetching_document_info")

        # Get document information
        document_data = await self.document_repo.get_by_id(document_id)
        if not document_data:
            raise ValueError(f"Document with id {document_id} not found")

        file_path = document_data.file_path
        if not file_path:
            raise ValueError(f"Document {document_id} has no file_path - download PDF first")

        self.logger.info(
            f"Extracting from document: {file_path}",
            extra={"document_id": document_id},
        )

        self.update_progress("processing_pdf")

        # Get company name for extraction
        from app.db.repositories.company import CompanyRepository

        company_repo = CompanyRepository(self.session)
        company = await company_repo.get_by_id(document_data.company_id)
        company_name = company.name if company else "Unknown Company"

        # Process PDF and extract text/tables using PDFExtractor
        extracted_content = await self._process_pdf(file_path)

        self.update_progress("calling_llm")

        # Extract financial statements using FinancialStatementExtractor
        statement_types = ["income_statement", "balance_sheet", "cash_flow_statement"]
        statements_data = {}

        for stmt_type in statement_types:
            try:
                extraction = await self.extractor.extract_statement(
                    extracted_content=extracted_content,
                    statement_type=stmt_type,
                    company_name=company_name,
                    fiscal_year=document_data.fiscal_year,
                    fiscal_year_end=f"{document_data.fiscal_year}-12-31",
                )

                # Convert to dict format for storage
                statements_data[stmt_type] = extraction.to_dict()

            except Exception as e:
                self.logger.warning(
                    f"Failed to extract {stmt_type}: {e}",
                    extra={"document_id": document_id, "statement_type": stmt_type},
                    exc_info=True,
                )
                # Continue with other statement types

        self.update_progress("storing_extractions")

        # Store extractions in database
        created_extractions = await self._store_extractions(document_id, statements_data)

        result = {
            "document_id": document_id,
            "status": "success",
            "extracted_statements": list(statements_data.keys()),
            "extraction_count": len(created_extractions),
            "extractions": created_extractions,
        }

        self.logger.info(
            "Completed extract_financial_statements",
            extra={"document_id": document_id, "result": result},
        )

        return result

    async def process_document(self, document_id: int) -> dict[str, Any]:
        """Process a document end-to-end: classify, download, and extract.

        This orchestrates multiple steps but delegates to other workers
        for actual execution. In a real implementation, this would coordinate
        with ScrapingWorker for classification and download.

        Args:
            document_id: ID of the document to process.

        Returns:
            Dictionary with task results from all processing steps.
        """
        self.logger.info("Starting process_document", extra={"document_id": document_id})

        # This method would coordinate with other workers
        # For now, we'll just extract (classification/download handled elsewhere)
        result = await self.extract_financial_statements(document_id)

        return {
            "document_id": document_id,
            "status": "success",
            "extraction": result,
        }

    async def execute(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        """Execute worker operation (required by BaseWorker).

        This worker has specific methods, so execute is not used directly.
        """
        raise NotImplementedError(
            "ExtractionWorker uses specific methods (extract_financial_statements, "
            "process_document) instead of execute"
        )

    # Helper methods

    async def _process_pdf(self, file_path: str) -> dict[str, Any]:
        """Process PDF file and extract text/tables using PDFExtractor.

        Handles both local file paths and object storage keys.

        Args:
            file_path: Path to PDF file or object key.

        Returns:
            Dictionary with extracted content and metadata.
        """
        from pathlib import Path

        # Determine if this is a local path or object storage key
        local_path = Path(file_path)
        is_local_file = local_path.exists()

        if is_local_file:
            # Local file handling
            return await self.pdf_extractor.extract_from_path(file_path)
        elif self.storage_service:
            # Object storage handling
            file_content = await self.storage_service.get_file(file_path)
            return await self.pdf_extractor.extract_from_storage(file_content, file_path)
        else:
            raise ValueError(
                f"Cannot open PDF: {file_path} (not local file and no storage service)"
            )

    async def _store_extractions(
        self, document_id: int, statements_data: dict[str, dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Store extractions in database.

        Args:
            document_id: Document ID.
            statements_data: Dictionary with statement types and extracted data.

        Returns:
            List of created extraction records as dictionaries.
        """
        created_extractions = []

        # Map statement type names to database format
        type_mapping = {
            "income_statement": "income_statement",
            "balance_sheet": "balance_sheet",
            "cash_flow_statement": "cash_flow_statement",
        }

        for stmt_type_key, stmt_data in statements_data.items():
            db_stmt_type = type_mapping.get(stmt_type_key, stmt_type_key)

            # Store raw_data in format expected by database
            # The stmt_data is already a dict from to_dict()
            extraction = await self.extraction_repo.create(
                document_id=document_id,
                statement_type=db_stmt_type,
                raw_data=stmt_data,
            )

            if extraction:
                created_extractions.append(await self.extraction_repo._model_to_dict(extraction))

        return created_extractions
