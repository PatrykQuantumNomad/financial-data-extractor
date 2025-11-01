"""
Celery tasks for web scraping and document discovery.

Tasks handle scraping investor relations websites, downloading PDFs,
and classifying documents.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

import asyncio
import logging
from pathlib import Path
from typing import Any

import httpx
from app.db.repositories.company import CompanyRepository
from app.db.repositories.document import DocumentRepository
from app.tasks.celery_app import celery_app
from app.tasks.utils import (calculate_file_hash, get_db_context,
                             get_pdf_storage_path, run_async,
                             validate_task_result)
from celery import Task
from celery.exceptions import Retry

logger = logging.getLogger(__name__)

# Default HTTP headers for polite web scraping
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}


@celery_app.task(
    bind=True,
    name="app.tasks.scraping_tasks.scrape_investor_relations",
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(httpx.HTTPError, httpx.TimeoutException, ConnectionError),
)
def scrape_investor_relations(self: Task, company_id: int) -> dict[str, Any]:
    """Scrape investor relations website to discover PDF documents.

    Args:
        company_id: ID of the company to scrape.

    Returns:
        Dictionary with task results including discovered documents.

    Raises:
        ValueError: If company not found or scraping fails.
    """
    task_id = self.request.id
    logger.info(
        f"Starting scrape_investor_relations task",
        extra={
            "task_id": task_id,
            "company_id": company_id,
        },
    )

    try:
        # Update task state
        self.update_state(state="PROGRESS", meta={"step": "fetching_company_info"})

        # Get company information
        company_data = run_async(_get_company_info(company_id))
        if not company_data:
            raise ValueError(f"Company with id {company_id} not found")

        ir_url = company_data["ir_url"]
        logger.info(
            f"Scraping IR website: {ir_url}",
            extra={"task_id": task_id, "company_id": company_id, "url": ir_url},
        )

        # Update task state
        self.update_state(state="PROGRESS", meta={"step": "scraping_website"})

        # Scrape website for PDFs
        # TODO: Implement actual scraping logic using BeautifulSoup
        # This is a placeholder that should be implemented based on specific website structure
        discovered_urls = run_async(_discover_pdf_urls(ir_url))

        logger.info(
            f"Discovered {len(discovered_urls)} PDF URLs",
            extra={"task_id": task_id, "company_id": company_id, "count": len(discovered_urls)},
        )

        # Update task state
        self.update_state(state="PROGRESS", meta={"step": "creating_document_records", "discovered": len(discovered_urls)})

        # Create document records for discovered PDFs
        created_documents = run_async(_create_document_records(company_id, discovered_urls))

        result = {
            "task_id": task_id,
            "company_id": company_id,
            "status": "success",
            "discovered_count": len(discovered_urls),
            "created_count": len(created_documents),
            "documents": created_documents,
        }

        validate_task_result(result, ["task_id", "company_id", "status"])
        logger.info(f"Completed scrape_investor_relations task", extra={"task_id": task_id, "result": result})

        return result

    except httpx.HTTPStatusError as e:
        # Handle 403 Forbidden specifically - don't retry, just log and return empty results
        if e.response.status_code == 403:
            logger.warning(
                f"403 Forbidden when scraping {company_id} - website blocking requests",
                extra={"task_id": task_id, "company_id": company_id, "url": ir_url},
            )
            # Return empty results instead of failing
            return {
                "task_id": task_id,
                "company_id": company_id,
                "status": "partial",
                "message": "Website returned 403 Forbidden - no documents discovered",
                "discovered_count": 0,
                "created_count": 0,
                "documents": [],
            }
        # For other HTTP errors, retry
        logger.error(
            f"HTTP error in scrape_investor_relations task: {e}",
            extra={"task_id": task_id, "company_id": company_id, "status_code": e.response.status_code},
            exc_info=True,
        )
        raise self.retry(exc=e)
    except Exception as e:
        logger.error(
            f"Failed scrape_investor_relations task: {e}",
            extra={"task_id": task_id, "company_id": company_id},
            exc_info=True,
        )
        # Retry on transient errors
        if isinstance(e, (httpx.HTTPError, httpx.TimeoutException, ConnectionError)):
            raise self.retry(exc=e)
        raise


@celery_app.task(
    bind=True,
    name="app.tasks.scraping_tasks.download_pdf",
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(httpx.HTTPError, httpx.TimeoutException, ConnectionError, FileNotFoundError),
)
def download_pdf(self: Task, document_id: int) -> dict[str, Any]:
    """Download PDF document from URL and store locally.

    Args:
        document_id: ID of the document to download.

    Returns:
        Dictionary with task results including file path and hash.

    Raises:
        ValueError: If document not found or download fails.
    """
    task_id = self.request.id
    logger.info(f"Starting download_pdf task", extra={"task_id": task_id, "document_id": document_id})

    try:
        # Update task state
        self.update_state(state="PROGRESS", meta={"step": "fetching_document_info"})

        # Get document information
        document_data = run_async(_get_document_info(document_id))
        if not document_data:
            raise ValueError(f"Document with id {document_id} not found")

        url = document_data["url"]
        company_id = document_data["company_id"]
        fiscal_year = document_data["fiscal_year"]

        logger.info(f"Downloading PDF from: {url}", extra={"task_id": task_id, "document_id": document_id})

        # Update task state
        self.update_state(state="PROGRESS", meta={"step": "downloading_file"})

        # Download PDF
        file_path, file_hash = run_async(_download_pdf_file(url, company_id, fiscal_year))

        # Update task state
        self.update_state(state="PROGRESS", meta={"step": "updating_database"})

        # Update document record with file path
        run_async(_update_document_file_path(document_id, str(file_path)))

        result = {
            "task_id": task_id,
            "document_id": document_id,
            "status": "success",
            "file_path": str(file_path),
            "file_hash": file_hash,
        }

        validate_task_result(result, ["task_id", "document_id", "status", "file_path"])
        logger.info(f"Completed download_pdf task", extra={"task_id": task_id, "result": result})

        return result

    except Exception as e:
        logger.error(
            f"Failed download_pdf task: {e}",
            extra={"task_id": task_id, "document_id": document_id},
            exc_info=True,
        )
        # Retry on transient errors
        if isinstance(e, (httpx.HTTPError, httpx.TimeoutException, ConnectionError)):
            raise self.retry(exc=e)
        raise


@celery_app.task(
    bind=True,
    name="app.tasks.scraping_tasks.classify_document",
    max_retries=2,
    default_retry_delay=30,
)
def classify_document(self: Task, document_id: int) -> dict[str, Any]:
    """Classify a document by type (annual_report, quarterly_report, etc.).

    Uses filename patterns, metadata, and content sampling to determine document type.

    Args:
        document_id: ID of the document to classify.

    Returns:
        Dictionary with task results including document type.

    Raises:
        ValueError: If document not found or classification fails.
    """
    task_id = self.request.id
    logger.info(f"Starting classify_document task", extra={"task_id": task_id, "document_id": document_id})

    try:
        # Update task state
        self.update_state(state="PROGRESS", meta={"step": "fetching_document_info"})

        # Get document information
        document_data = run_async(_get_document_info(document_id))
        if not document_data:
            raise ValueError(f"Document with id {document_id} not found")

        # Update task state
        self.update_state(state="PROGRESS", meta={"step": "analyzing_document"})

        # Classify document
        # TODO: Implement actual classification logic
        # This should use filename patterns, URL patterns, and optionally content sampling
        document_type = run_async(_classify_document_type(document_data))

        # Update task state
        self.update_state(state="PROGRESS", meta={"step": "updating_database"})

        # Update document record with classification
        run_async(_update_document_type(document_id, document_type))

        result = {
            "task_id": task_id,
            "document_id": document_id,
            "status": "success",
            "document_type": document_type,
        }

        validate_task_result(result, ["task_id", "document_id", "status", "document_type"])
        logger.info(f"Completed classify_document task", extra={"task_id": task_id, "result": result})

        return result

    except Exception as e:
        logger.error(
            f"Failed classify_document task: {e}",
            extra={"task_id": task_id, "document_id": document_id},
            exc_info=True,
        )
        raise


# Helper functions (async)

async def _get_company_info(company_id: int) -> dict[str, Any] | None:
    """Get company information from database."""
    async with get_db_context() as pool:
        repo = CompanyRepository(pool)
        return await repo.get_by_id(company_id)


async def _get_document_info(document_id: int) -> dict[str, Any] | None:
    """Get document information from database."""
    async with get_db_context() as pool:
        repo = DocumentRepository(pool)
        return await repo.get_by_id(document_id)


async def _discover_pdf_urls(ir_url: str) -> list[dict[str, Any]]:
    """Discover PDF URLs from investor relations website.

    TODO: Implement actual scraping logic.
    This should use BeautifulSoup to parse HTML and find PDF links.

    Args:
        ir_url: Investor relations website URL.

    Returns:
        List of dictionaries with URL, filename, and metadata.

    Raises:
        httpx.HTTPStatusError: If HTTP request fails (403, 404, etc.)
    """
    # Add polite delay before scraping (respect rate limits)
    await asyncio.sleep(1.0)  # 1 second delay

    # Placeholder implementation
    # Should use BeautifulSoup to scrape and find PDF links
    async with httpx.AsyncClient(
        timeout=httpx.Timeout(30.0, connect=10.0),
        headers=DEFAULT_HEADERS,
        follow_redirects=True,
        max_redirects=5,
    ) as client:
        try:
            response = await client.get(ir_url)

            # Handle 403 Forbidden specifically
            if response.status_code == 403:
                logger.warning(
                    f"Got 403 Forbidden for {ir_url} - website may be blocking requests",
                    extra={"url": ir_url, "status_code": 403},
                )
                # Don't raise - return empty list instead
                # This allows the task to complete without error
                return []

            response.raise_for_status()

            # TODO: Parse HTML and extract PDF links using BeautifulSoup
            # For now, return empty list
            return []

        except httpx.HTTPStatusError as e:
            # Log the error but don't fail silently for non-403 errors
            if e.response.status_code == 403:
                logger.warning(
                    f"403 Forbidden for {ir_url} - skipping",
                    extra={"url": ir_url},
                )
                return []
            # Re-raise for other HTTP errors
            raise


async def _create_document_records(company_id: int, urls: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Create document records in database for discovered URLs."""
    created_documents = []
    async with get_db_context() as pool:
        repo = DocumentRepository(pool)
        for url_data in urls:
            # Extract fiscal year from URL or metadata if available
            fiscal_year = url_data.get("fiscal_year", 2024)  # Default fallback
            document_type = url_data.get("document_type", "unknown")

            document = await repo.create(
                company_id=company_id,
                url=url_data["url"],
                fiscal_year=fiscal_year,
                document_type=document_type,
                file_path=None,
            )
            if document:
                created_documents.append(document)
    return created_documents


async def _download_pdf_file(url: str, company_id: int, fiscal_year: int) -> tuple[Path, str]:
    """Download PDF file and store locally.

    Args:
        url: URL of the PDF to download.
        company_id: Company ID for storage path.
        fiscal_year: Fiscal year for storage path.

    Returns:
        Tuple of (file_path, file_hash).

    Raises:
        httpx.HTTPStatusError: If download fails.
    """
    # Add polite delay before download
    await asyncio.sleep(1.0)

    async with httpx.AsyncClient(
        timeout=httpx.Timeout(120.0, connect=10.0),
        headers=DEFAULT_HEADERS,
        follow_redirects=True,
        max_redirects=5,
    ) as client:
        response = await client.get(url)

        # Handle 403 Forbidden
        if response.status_code == 403:
            logger.warning(
                f"Got 403 Forbidden when downloading PDF from {url}",
                extra={"url": url, "company_id": company_id},
            )
            raise httpx.HTTPStatusError(
                "403 Forbidden - PDF download blocked",
                request=response.request,
                response=response,
            )

        response.raise_for_status()

        # Extract filename from URL or Content-Disposition header
        filename = url.split("/")[-1] or "document.pdf"
        if not filename.endswith(".pdf"):
            filename = f"{filename}.pdf"

        # Get storage path
        file_path = get_pdf_storage_path(company_id, fiscal_year, filename)

        # Save file
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(response.content)

        # Calculate hash
        file_hash = calculate_file_hash(file_path)

        return file_path, file_hash


async def _update_document_file_path(document_id: int, file_path: str) -> None:
    """Update document record with file path."""
    async with get_db_context() as pool:
        repo = DocumentRepository(pool)
        # Use execute_update directly for file_path update
        query = "UPDATE documents SET file_path = %(file_path)s WHERE id = %(document_id)s"
        await repo.execute_update(query, {"file_path": file_path, "document_id": document_id})


async def _classify_document_type(document_data: dict[str, Any]) -> str:
    """Classify document type based on URL, filename, and content.

    TODO: Implement actual classification logic.
    Should check:
    - Filename patterns (annual, quarterly, presentation, etc.)
    - URL patterns
    - Optionally sample PDF content

    Args:
        document_data: Document information dictionary.

    Returns:
        Document type string.
    """
    url = document_data.get("url", "").lower()
    file_path = document_data.get("file_path", "").lower()

    # Simple classification based on keywords
    if any(keyword in url or keyword in file_path for keyword in ["annual", "ar", "year"]):
        return "annual_report"
    elif any(keyword in url or keyword in file_path for keyword in ["quarterly", "q", "quarter"]):
        return "quarterly_report"
    elif any(keyword in url or keyword in file_path for keyword in ["presentation", "investor"]):
        return "investor_presentation"
    else:
        return "unknown"


async def _update_document_type(document_id: int, document_type: str) -> None:
    """Update document record with document type."""
    async with get_db_context() as pool:
        repo = DocumentRepository(pool)
        query = "UPDATE documents SET document_type = %(document_type)s WHERE id = %(document_id)s"
        await repo.execute_update(query, {"document_type": document_type, "document_id": document_id})
