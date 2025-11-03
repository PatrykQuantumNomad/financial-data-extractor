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
from app.core.storage import IStorageService
from app.db.models.document import Document
from app.db.repositories.company import CompanyRepository
from app.db.repositories.document import DocumentRepository
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
        storage_service: IStorageService | None = None,
    ):
        """Initialize scraping worker.

        Args:
            session: Database async session.
            progress_callback: Optional callback for progress updates.
            storage_service: Optional storage service for PDF files.
        """
        super().__init__(progress_callback)
        self.session = session
        self.company_repo = CompanyRepository(session)
        self.document_repo = DocumentRepository(session)
        self.storage_service = storage_service

    async def scrape_investor_relations(
        self, company_id: int, openrouter_api_key: str | None = None
    ) -> dict[str, Any]:
        """Scrape investor relations website to discover and download PDF documents.

        Performs deep crawling to discover PDFs across multiple pages, then automatically
        downloads them during the discovery process.

        Args:
            company_id: ID of the company to scrape.
            openrouter_api_key: Optional OpenRouter API key for LLM extraction.

        Returns:
            Dictionary with task results including discovered and downloaded documents.

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

        ir_url = company_data.ir_url
        self.logger.info(
            f"Scraping IR website: {ir_url}",
            extra={"company_id": company_id, "url": ir_url},
        )

        self.update_progress("deep_crawling_website")

        # Discover PDF URLs using deep crawling
        discovered_pdfs = await self._discover_pdf_urls(ir_url, openrouter_api_key)

        self.logger.info(
            f"Discovered {len(discovered_pdfs)} PDF URLs",
            extra={"company_id": company_id, "count": len(discovered_pdfs)},
        )

        self.update_progress("downloading_pdfs", {"discovered": len(discovered_pdfs)})

        # Download discovered PDFs and create document records
        created_documents = await self._download_and_create_documents(company_id, discovered_pdfs)

        result = {
            "company_id": company_id,
            "status": "success",
            "discovered_count": len(discovered_pdfs),
            "created_count": len(created_documents),
            "downloaded_count": sum(1 for doc in created_documents if doc.get("file_path")),
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

        url = document_data.url
        company_id = document_data.company_id
        fiscal_year = document_data.fiscal_year

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
        self, ir_url: str, openrouter_api_key: str | None = None
    ) -> list[dict[str, Any]]:
        """Discover PDF URLs from investor relations website using Crawl4AI deep crawling.

        Args:
            ir_url: Investor relations website URL.
            openrouter_api_key: Optional OpenRouter API key for LLM extraction.

        Returns:
            List of dictionaries with URL, filename, fiscal_year, etc.
        """
        self.logger.info(
            f"Starting PDF discovery for {ir_url}",
            extra={"url": ir_url, "use_llm": openrouter_api_key is not None},
        )

        try:
            # Use Crawl4AI scraping service with OpenRouter
            async with ScrapingService(openrouter_api_key=openrouter_api_key) as service:
                # Discover PDFs using deep crawling
                use_llm = openrouter_api_key is not None
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

    async def _download_and_create_documents(
        self, company_id: int, pdfs: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Download discovered PDFs and create document records.

        Downloads each PDF, validates it, and creates database records with file paths.

        Args:
            company_id: Company ID.
            pdfs: List of discovered PDF dictionaries with metadata.

        Returns:
            List of created document records as dictionaries.
        """
        created_documents = []

        for i, pdf_data in enumerate(pdfs):
            url = pdf_data.get("url", "")
            # Handle None explicitly - fiscal_year is required in DB
            fiscal_year = pdf_data.get("fiscal_year") or self._extract_fiscal_year_from_url(url)
            if fiscal_year is None:
                self.logger.warning(
                    f"Cannot extract fiscal year from URL: {url}, skipping document",
                    extra={"url": url},
                )
                continue  # Skip documents without fiscal year
            document_type = pdf_data.get("document_type", "unknown")

            # Update progress
            self.update_progress(
                "downloading_pdfs",
                {"current": i + 1, "total": len(pdfs)},
            )

            # Create document record first
            document = await self.document_repo.create(
                company_id=company_id,
                url=url,
                fiscal_year=fiscal_year,
                document_type=document_type,
                file_path=None,  # Will be updated after download
            )

            if not document:
                continue

            # Download PDF with retry logic
            try:
                storage_path, file_hash = await self._download_pdf_file(
                    url, company_id, fiscal_year
                )

                # Validate PDF file
                if not self._validate_pdf_content(await self._get_pdf_content(storage_path)):
                    self.logger.warning(
                        f"Invalid PDF file: {storage_path}, removing it",
                        extra={"document_id": document.id},
                    )
                    await self.storage_service.delete_file(storage_path)
                    continue

                # Update document with storage path
                updated_doc = await self.document_repo.update(
                    document_id=document.id, file_path=storage_path
                )

                if updated_doc:
                    created_documents.append(await self.document_repo._model_to_dict(updated_doc))

                self.logger.info(
                    f"Downloaded PDF: {storage_path}",
                    extra={"document_id": document.id, "url": url},
                )

            except Exception as e:
                self.logger.error(
                    f"Failed to download PDF from {url}: {e}",
                    extra={"document_id": document.id, "url": url},
                )
                # Document still created but without file_path
                created_documents.append(await self.document_repo._model_to_dict(document))

        return created_documents

    async def _create_document_records(
        self, company_id: int, urls: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Create document records in database for discovered URLs.

        Args:
            company_id: Company ID.
            urls: List of URL dictionaries with metadata.

        Returns:
            List of created document records as dictionaries.
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
                created_documents.append(await self.document_repo._model_to_dict(document))
        return created_documents

    async def _download_pdf_file(
        self, url: str, company_id: int, fiscal_year: int
    ) -> tuple[str, str]:
        """Download PDF file and store in object storage or local filesystem.

        Args:
            url: URL of the PDF to download.
            company_id: Company ID for storage path.
            fiscal_year: Fiscal year for storage path.

        Returns:
            Tuple of (storage_path, file_hash).

        Raises:
            httpx.HTTPStatusError: If download fails.
        """
        if not self.storage_service:
            raise RuntimeError("Storage service not initialized")

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

            # Create object key for storage
            object_key = f"company_{company_id}/{fiscal_year}/{filename}"

            # Save file using storage service
            storage_path = await self.storage_service.save_file(
                file_content=response.content,
                object_key=object_key,
                content_type="application/pdf",
            )

            # Calculate hash using storage service
            file_hash = await self.storage_service.calculate_file_hash(object_key)

            return storage_path, file_hash

    async def _get_pdf_content(self, storage_path: str) -> bytes:
        """Get PDF content from storage for validation.

        Args:
            storage_path: Storage path or object key.

        Returns:
            PDF file content as bytes.
        """
        if not self.storage_service:
            raise RuntimeError("Storage service not initialized")
        return await self.storage_service.get_file(storage_path)

    def _validate_pdf_content(self, file_content: bytes) -> bool:
        """Validate that file content is a valid PDF by checking magic bytes.

        Args:
            file_content: File content as bytes.

        Returns:
            True if content is a valid PDF, False otherwise.
        """
        try:
            # Check if file is too small (likely not a PDF)
            if len(file_content) < 100:
                return False

            # Check PDF magic bytes (%PDF)
            return file_content[:4] == b"%PDF"
        except Exception as e:
            self.logger.error(
                f"Error validating PDF content: {e}",
                exc_info=True,
            )
            return False

    def _validate_pdf_file(self, file_path: Path) -> bool:
        """Validate that a file is a valid PDF by checking magic bytes (legacy method).

        Args:
            file_path: Path to the file to validate.

        Returns:
            True if file is a valid PDF, False otherwise.
        """
        try:
            if not file_path.exists():
                return False

            # Check if file is too small (likely not a PDF)
            if file_path.stat().st_size < 100:
                return False

            # Check PDF magic bytes (%PDF)
            with open(file_path, "rb") as f:
                header = f.read(4)
                return header == b"%PDF"
        except Exception as e:
            self.logger.error(
                f"Error validating PDF file {file_path}: {e}",
                exc_info=True,
            )
            return False

    def _extract_fiscal_year_from_url(self, url: str) -> int | None:
        """Extract fiscal year from URL using pattern matching.

        Handles various formats like:
        - "AstraZeneca_AR_2017 (1).pdf" -> 2017
        - "annual-report-2024.pdf" -> 2024
        - "2023_Annual_Report" -> 2023

        Args:
            url: URL to extract fiscal year from.

        Returns:
            Fiscal year if found, None otherwise.
        """
        import re

        if not url:
            return None

        # Look for 4-digit years (2000-2099) - improved pattern
        # Matches years even with special characters like parentheses
        year_pattern = r"(?:^|[^0-9])(20[0-2][0-9])(?:[^0-9]|$)"
        matches = re.findall(year_pattern, url)

        if matches:
            # Return the most recent year found (typically the fiscal year)
            years = [int(y) for y in matches]
            # Filter to reasonable range (2000-2099, with practical limits)
            years = [y for y in years if 2000 <= y <= 2099]
            if years:
                return max(years)

        return None

    async def _classify_document_type(self, document: Document) -> str:
        """Classify document type based on URL, filename, and content.

        Args:
            document: Document model instance.

        Returns:
            Document type string.
        """
        url = (document.url or "").lower()
        file_path = (document.file_path or "").lower()

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
