"""
Worker for web scraping and document discovery.

Extracts business logic from scraping tasks for testability.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

import asyncio
import logging
from pathlib import Path
from typing import Any

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.scraping import ScrapingService
from app.db.repositories.company import CompanyRepository
from app.db.repositories.document import DocumentRepository
from app.tasks.utils import calculate_file_hash, get_pdf_storage_path
from app.workers.base import BaseWorker

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


class ScrapingWorker(BaseWorker):
    """Worker for scraping investor relations websites and managing documents.

    Handles:
    - Scraping IR websites for PDF discovery
    - Downloading PDF documents
    - Classifying documents by type
    """

    def __init__(
        self,
        session: AsyncSession,
        progress_callback: Any | None = None,
    ):
        """Initialize scraping worker.

        Args:
            session: Database async session.
            progress_callback: Optional callback for progress updates.
        """
        super().__init__(progress_callback)
        self.session = session
        self.company_repo = CompanyRepository(session)
        self.document_repo = DocumentRepository(session)

    async def scrape_investor_relations(
        self, company_id: int, openai_api_key: str | None = None
    ) -> dict[str, Any]:
        """Scrape investor relations website to discover PDF documents.

        Args:
            company_id: ID of the company to scrape.
            openai_api_key: Optional OpenAI API key for LLM extraction.

        Returns:
            Dictionary with task results including discovered documents.

        Raises:
            ValueError: If company not found.
            httpx.HTTPStatusError: If scraping fails (except 403).
        """
        self.logger.info(
            "Starting scrape_investor_relations",
            extra={"company_id": company_id},
        )

        self.update_progress("fetching_company_info")

        # Get company information
        company_data = await self.company_repo.get_by_id(company_id)
        if not company_data:
            raise ValueError(f"Company with id {company_id} not found")

        ir_url = company_data["ir_url"]
        self.logger.info(
            f"Scraping IR website: {ir_url}",
            extra={"company_id": company_id, "url": ir_url},
        )

        self.update_progress("scraping_website")

        # Discover PDF URLs
        discovered_urls = await self._discover_pdf_urls(ir_url, openai_api_key)

        self.logger.info(
            f"Discovered {len(discovered_urls)} PDF URLs",
            extra={"company_id": company_id, "count": len(discovered_urls)},
        )

        self.update_progress("creating_document_records", {"discovered": len(discovered_urls)})

        # Create document records
        created_documents = await self._create_document_records(company_id, discovered_urls)

        result = {
            "company_id": company_id,
            "status": "success",
            "discovered_count": len(discovered_urls),
            "created_count": len(created_documents),
            "documents": created_documents,
        }

        self.logger.info(
            "Completed scrape_investor_relations",
            extra={"company_id": company_id, "result": result},
        )

        return result

    async def download_pdf(self, document_id: int) -> dict[str, Any]:
        """Download PDF document from URL and store locally.

        Args:
            document_id: ID of the document to download.

        Returns:
            Dictionary with task results including file path and hash.

        Raises:
            ValueError: If document not found.
            httpx.HTTPStatusError: If download fails.
        """
        self.logger.info("Starting download_pdf", extra={"document_id": document_id})

        self.update_progress("fetching_document_info")

        # Get document information
        document_data = await self.document_repo.get_by_id(document_id)
        if not document_data:
            raise ValueError(f"Document with id {document_id} not found")

        url = document_data["url"]
        company_id = document_data["company_id"]
        fiscal_year = document_data["fiscal_year"]

        self.logger.info(
            f"Downloading PDF from: {url}",
            extra={"document_id": document_id},
        )

        self.update_progress("downloading_file")

        # Download PDF
        file_path, file_hash = await self._download_pdf_file(url, company_id, fiscal_year)

        self.update_progress("updating_database")

        # Update document record with file path
        await self.document_repo.update(document_id=document_id, file_path=str(file_path))

        result = {
            "document_id": document_id,
            "status": "success",
            "file_path": str(file_path),
            "file_hash": file_hash,
        }

        self.logger.info(
            "Completed download_pdf",
            extra={"document_id": document_id, "result": result},
        )

        return result

    async def classify_document(self, document_id: int) -> dict[str, Any]:
        """Classify a document by type (annual_report, quarterly_report, etc.).

        Args:
            document_id: ID of the document to classify.

        Returns:
            Dictionary with task results including document type.

        Raises:
            ValueError: If document not found.
        """
        self.logger.info("Starting classify_document", extra={"document_id": document_id})

        self.update_progress("fetching_document_info")

        # Get document information
        document_data = await self.document_repo.get_by_id(document_id)
        if not document_data:
            raise ValueError(f"Document with id {document_id} not found")

        self.update_progress("analyzing_document")

        # Classify document
        document_type = await self._classify_document_type(document_data)

        self.update_progress("updating_database")

        # Update document record with classification
        await self.document_repo.update(document_id=document_id, document_type=document_type)

        result = {
            "document_id": document_id,
            "status": "success",
            "document_type": document_type,
        }

        self.logger.info(
            "Completed classify_document",
            extra={"document_id": document_id, "result": result},
        )

        return result

    async def execute(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        """Execute worker operation (required by BaseWorker).

        This worker has specific methods, so execute is not used directly.
        """
        raise NotImplementedError(
            "ScrapingWorker uses specific methods (scrape_investor_relations, "
            "download_pdf, classify_document) instead of execute"
        )

    # Helper methods

    async def _discover_pdf_urls(
        self, ir_url: str, openai_api_key: str | None = None
    ) -> list[dict[str, Any]]:
        """Discover PDF URLs from investor relations website using Crawl4AI.

        Args:
            ir_url: Investor relations website URL.
            openai_api_key: Optional OpenAI API key for LLM extraction.

        Returns:
            List of dictionaries with URL, filename, fiscal_year, etc.
        """
        self.logger.info(
            f"Starting PDF discovery for {ir_url}",
            extra={"url": ir_url, "use_llm": openai_api_key is not None},
        )

        try:
            # Use Crawl4AI scraping service
            async with ScrapingService(openai_api_key=openai_api_key) as service:
                # Discover PDFs
                use_llm = openai_api_key is not None
                discovered_pdfs = await service.discover_pdf_urls(ir_url, use_llm=use_llm)

                # Convert DiscoveredPDF objects to dictionaries
                pdf_dicts = []
                for pdf in discovered_pdfs:
                    pdf_dicts.append(
                        {
                            "url": pdf.url,
                            "filename": pdf.filename,
                            "fiscal_year": pdf.fiscal_year,
                            "document_type": pdf.document_type,
                            "title": pdf.title,
                            "description": pdf.description,
                            "confidence": pdf.confidence,
                        }
                    )

                self.logger.info(
                    f"Successfully discovered {len(pdf_dicts)} PDFs from {ir_url}",
                    extra={"url": ir_url, "count": len(pdf_dicts)},
                )

                return pdf_dicts

        except Exception as e:
            self.logger.error(
                f"Failed to discover PDFs from {ir_url}: {e}",
                exc_info=True,
                extra={"url": ir_url},
            )
            raise

    async def _create_document_records(
        self, company_id: int, urls: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Create document records in database for discovered URLs.

        Args:
            company_id: Company ID.
            urls: List of URL dictionaries with metadata.

        Returns:
            List of created document records.
        """
        created_documents = []
        for url_data in urls:
            # Extract fiscal year from URL or metadata if available
            fiscal_year = url_data.get("fiscal_year", 2024)  # Default fallback
            document_type = url_data.get("document_type", "unknown")

            document = await self.document_repo.create(
                company_id=company_id,
                url=url_data["url"],
                fiscal_year=fiscal_year,
                document_type=document_type,
                file_path=None,
            )
            if document:
                created_documents.append(document)
        return created_documents

    async def _download_pdf_file(
        self, url: str, company_id: int, fiscal_year: int
    ) -> tuple[Path, str]:
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
                self.logger.warning(
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

    async def _classify_document_type(self, document_data: dict[str, Any]) -> str:
        """Classify document type based on URL, filename, and content.

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
        elif any(
            keyword in url or keyword in file_path for keyword in ["quarterly", "q", "quarter"]
        ):
            return "quarterly_report"
        elif any(
            keyword in url or keyword in file_path for keyword in ["presentation", "investor"]
        ):
            return "investor_presentation"
        else:
            return "unknown"
