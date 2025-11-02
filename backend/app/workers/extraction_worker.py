"""
Worker for financial statement extraction from PDFs.

Extracts business logic from extraction tasks for testability.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

import json
import logging
from typing import Any

from openai import OpenAI
from sqlalchemy.ext.asyncio import AsyncSession

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
        openai_client: OpenAI | None = None,
        progress_callback: Any | None = None,
    ):
        """Initialize extraction worker.

        Args:
            session: Database async session.
            openai_client: Optional OpenAI client (will be created if not provided).
            progress_callback: Optional callback for progress updates.
        """
        super().__init__(progress_callback)
        self.session = session
        self.document_repo = DocumentRepository(session)
        self.extraction_repo = ExtractionRepository(session)
        self.openai_client = openai_client

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

        file_path = document_data.get("file_path")
        if not file_path:
            raise ValueError(f"Document {document_id} has no file_path - download PDF first")

        self.logger.info(
            f"Extracting from document: {file_path}",
            extra={"document_id": document_id},
        )

        self.update_progress("processing_pdf")

        # Process PDF and extract text/tables
        extracted_content = await self._process_pdf(file_path)

        self.update_progress("calling_llm")

        # Extract financial statements using LLM
        statements_data = await self._extract_with_llm(extracted_content)

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
        """Process PDF file and extract text/tables.

        Args:
            file_path: Path to PDF file.

        Returns:
            Dictionary with extracted content and metadata.
        """
        try:
            import fitz  # PyMuPDF

            doc = fitz.open(file_path)
            text_content = []
            tables = []
            page_count = len(doc)

            for page_num in range(page_count):
                page = doc[page_num]
                text_content.append(page.get_text())

                # TODO: Extract tables from page
                # This requires table detection logic

            doc.close()

            return {
                "text": "\n\n".join(text_content),
                "tables": tables,
                "page_count": page_count,
            }
        except ImportError:
            self.logger.warning("PyMuPDF not available, using basic text extraction")
            # Fallback: return minimal structure
            return {
                "text": "",
                "tables": [],
                "page_count": 0,
            }

    async def _extract_with_llm(
        self, extracted_content: dict[str, Any]
    ) -> dict[str, dict[str, Any]]:
        """Extract financial statements using OpenAI GPT.

        Args:
            extracted_content: Dictionary with PDF text and tables.

        Returns:
            Dictionary with statement types as keys and extracted data as values.
        """
        if not self.openai_client:
            from config import Settings

            settings = Settings()
            self.openai_client = OpenAI(api_key=settings.openai_api_key)

        # Build prompt for financial statement extraction
        prompt = self._build_extraction_prompt(extracted_content)

        # Call OpenAI API
        response = self.openai_client.chat.completions.create(
            model="gpt-4-turbo-preview",  # Will use GPT-5 when available
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a financial data extraction expert. "
                        "Extract Income Statement, Balance Sheet, and Cash Flow Statement data "
                        "from the provided document content. Return structured JSON with all line items and values."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.0,  # Deterministic output
            response_format={"type": "json_object"},
            max_tokens=8000,
        )

        # Parse response
        content = response.choices[0].message.content
        if not content:
            raise ValueError("Empty response from LLM")

        statements_data = json.loads(content)

        # Validate and normalize structure
        normalized_data = self._normalize_llm_response(statements_data)

        return normalized_data

    def _build_extraction_prompt(self, extracted_content: dict[str, Any]) -> str:
        """Build prompt for LLM extraction.

        Args:
            extracted_content: Dictionary with PDF text and tables.

        Returns:
            Formatted prompt string.
        """
        text = extracted_content.get("text", "")
        # Limit text length to avoid token limits
        # TODO: Implement smart truncation (focus on financial statement sections)
        text_preview = text[:50000] if len(text) > 50000 else text

        prompt = f"""Extract financial statements from the following document content.

Extract three types of financial statements:
1. Income Statement (also called P&L or Statement of Operations)
2. Balance Sheet (also called Statement of Financial Position)
3. Cash Flow Statement (also called Statement of Cash Flows)

For each statement, extract:
- All line items with their values
- Years/periods present in the statement
- Unit (e.g., millions, thousands)
- Currency

Return JSON in this format:
{{
    "income_statement": {{
        "line_items": [
            {{"name": "Revenue", "2023": 1000, "2022": 900, "unit": "millions", "currency": "EUR"}},
            ...
        ],
        "years": [2023, 2022, 2021],
        "unit": "millions",
        "currency": "EUR"
    }},
    "balance_sheet": {{...}},
    "cash_flow_statement": {{...}}
}}

Document content:
{text_preview}
"""

        return prompt

    def _normalize_llm_response(self, statements_data: dict[str, Any]) -> dict[str, dict[str, Any]]:
        """Normalize LLM response to expected structure.

        Args:
            statements_data: Raw LLM response.

        Returns:
            Normalized dictionary with statement types as keys.
        """
        normalized = {}
        statement_types = ["income_statement", "balance_sheet", "cash_flow_statement"]

        for stmt_type in statement_types:
            if stmt_type in statements_data:
                normalized[stmt_type] = statements_data[stmt_type]
            else:
                # Try alternative names
                alternatives = {
                    "income_statement": ["income", "profit_loss", "pl", "operations"],
                    "balance_sheet": ["balance", "financial_position"],
                    "cash_flow_statement": ["cash_flow", "cashflow", "cash"],
                }
                for alt in alternatives.get(stmt_type, []):
                    if alt in statements_data:
                        normalized[stmt_type] = statements_data[alt]
                        break

        return normalized

    async def _store_extractions(
        self, document_id: int, statements_data: dict[str, dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Store extractions in database.

        Args:
            document_id: Document ID.
            statements_data: Dictionary with statement types and extracted data.

        Returns:
            List of created extraction records.
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

            extraction = await self.extraction_repo.create(
                document_id=document_id,
                statement_type=db_stmt_type,
                raw_data=stmt_data,
            )

            if extraction:
                created_extractions.append(extraction)

        return created_extractions
