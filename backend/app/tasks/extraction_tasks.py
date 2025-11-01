"""
Celery tasks for financial statement extraction from PDFs.

Tasks handle PDF processing, LLM extraction, and storing raw extraction data.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

import json
import logging
from typing import Any

from celery import Task
from openai import OpenAI

from app.db.repositories.document import DocumentRepository
from app.db.repositories.extraction import ExtractionRepository
from app.tasks.celery_app import celery_app
from app.tasks.utils import get_db_context, run_async, validate_task_result
from config import Settings

logger = logging.getLogger(__name__)

# OpenAI client - initialized on first use
_openai_client: OpenAI | None = None


def get_openai_client() -> OpenAI:
    """Get or create OpenAI client.

    Returns:
        OpenAI client instance.
    """
    global _openai_client
    if _openai_client is None:
        settings = Settings()
        _openai_client = OpenAI(api_key=settings.openai_api_key)
    return _openai_client


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
    logger.info(f"Starting extract_financial_statements task", extra={"task_id": task_id, "document_id": document_id})

    try:
        # Update task state
        self.update_state(state="PROGRESS", meta={"step": "fetching_document_info"})

        # Get document information
        document_data = run_async(_get_document_info(document_id))
        if not document_data:
            raise ValueError(f"Document with id {document_id} not found")

        file_path = document_data.get("file_path")
        if not file_path:
            raise ValueError(f"Document {document_id} has no file_path - download PDF first")

        logger.info(f"Extracting from document: {file_path}", extra={"task_id": task_id, "document_id": document_id})

        # Update task state
        self.update_state(state="PROGRESS", meta={"step": "processing_pdf"})

        # Process PDF and extract text/tables
        extracted_content = run_async(_process_pdf(file_path))

        # Update task state
        self.update_state(state="PROGRESS", meta={"step": "calling_llm"})

        # Extract financial statements using LLM
        statements_data = run_async(_extract_with_llm(extracted_content))

        # Update task state
        self.update_state(state="PROGRESS", meta={"step": "storing_extractions"})

        # Store extractions in database
        created_extractions = run_async(_store_extractions(document_id, statements_data))

        result = {
            "task_id": task_id,
            "document_id": document_id,
            "status": "success",
            "extracted_statements": list(statements_data.keys()),
            "extraction_count": len(created_extractions),
            "extractions": created_extractions,
        }

        validate_task_result(result, ["task_id", "document_id", "status", "extracted_statements"])
        logger.info(f"Completed extract_financial_statements task", extra={"task_id": task_id, "result": result})

        return result

    except Exception as e:
        logger.error(
            f"Failed extract_financial_statements task: {e}",
            extra={"task_id": task_id, "document_id": document_id},
            exc_info=True,
        )
        # Retry on transient errors
        if isinstance(e, (ConnectionError, TimeoutError)):
            raise self.retry(exc=e)
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
    logger.info(f"Starting process_document task", extra={"task_id": task_id, "document_id": document_id})

    try:
        # Update task state
        self.update_state(state="PROGRESS", meta={"step": "classifying"})

        # Classify document
        from app.tasks.scraping_tasks import classify_document

        classify_result = classify_document.apply(args=[document_id]).get()

        # Update task state
        self.update_state(state="PROGRESS", meta={"step": "downloading"})

        # Download PDF if not already downloaded
        document_data = run_async(_get_document_info(document_id))
        if document_data and not document_data.get("file_path"):
            from app.tasks.scraping_tasks import download_pdf

            download_result = download_pdf.apply(args=[document_id]).get()
        else:
            download_result = {"status": "skipped", "reason": "file_already_exists"}

        # Update task state
        self.update_state(state="PROGRESS", meta={"step": "extracting"})

        # Extract financial statements (only for annual reports)
        if classify_result.get("document_type") == "annual_report":
            extract_result = extract_financial_statements.apply(args=[document_id]).get()
        else:
            extract_result = {"status": "skipped", "reason": "not_annual_report"}

        result = {
            "task_id": task_id,
            "document_id": document_id,
            "status": "success",
            "classification": classify_result,
            "download": download_result,
            "extraction": extract_result,
        }

        validate_task_result(result, ["task_id", "document_id", "status"])
        logger.info(f"Completed process_document task", extra={"task_id": task_id, "result": result})

        return result

    except Exception as e:
        logger.error(
            f"Failed process_document task: {e}",
            extra={"task_id": task_id, "document_id": document_id},
            exc_info=True,
        )
        raise


# Helper functions (async)

async def _get_document_info(document_id: int) -> dict[str, Any] | None:
    """Get document information from database."""
    async with get_db_context() as pool:
        repo = DocumentRepository(pool)
        return await repo.get_by_id(document_id)


async def _process_pdf(file_path: str) -> dict[str, Any]:
    """Process PDF file and extract text/tables.

    TODO: Implement actual PDF processing using PyMuPDF or pdfplumber.
    This should extract:
    - Text content
    - Tables (especially financial statement tables)
    - Metadata (pages, structure)

    Args:
        file_path: Path to PDF file.

    Returns:
        Dictionary with extracted content and metadata.
    """
    # Placeholder implementation
    # Should use PyMuPDF or pdfplumber to extract text and tables
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
        logger.warning("PyMuPDF not available, using basic text extraction")
        # Fallback: return minimal structure
        return {
            "text": "",
            "tables": [],
            "page_count": 0,
        }


async def _extract_with_llm(extracted_content: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Extract financial statements using OpenAI GPT-5.

    Args:
        extracted_content: Dictionary with PDF text and tables.

    Returns:
        Dictionary with statement types as keys and extracted data as values.
    """
    client = get_openai_client()

    # Build prompt for financial statement extraction
    prompt = _build_extraction_prompt(extracted_content)

    # Call OpenAI API
    # TODO: Use GPT-5 when available, fallback to GPT-4
    response = client.chat.completions.create(
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
    normalized_data = _normalize_llm_response(statements_data)

    return normalized_data


def _build_extraction_prompt(extracted_content: dict[str, Any]) -> str:
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


def _normalize_llm_response(statements_data: dict[str, Any]) -> dict[str, dict[str, Any]]:
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
    document_id: int, statements_data: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    """Store extractions in database.

    Args:
        document_id: Document ID.
        statements_data: Dictionary with statement types and extracted data.

    Returns:
        List of created extraction records.
    """
    created_extractions = []
    async with get_db_context() as pool:
        repo = ExtractionRepository(pool)

        # Map statement type names to database format
        type_mapping = {
            "income_statement": "income_statement",
            "balance_sheet": "balance_sheet",
            "cash_flow_statement": "cash_flow_statement",
        }

        for stmt_type_key, stmt_data in statements_data.items():
            db_stmt_type = type_mapping.get(stmt_type_key, stmt_type_key)

            extraction = await repo.create(
                document_id=document_id,
                statement_type=db_stmt_type,
                raw_data=stmt_data,
            )

            if extraction:
                created_extractions.append(extraction)

    return created_extractions
