"""
Scraping service using Crawl4AI for intelligent PDF discovery.

This service uses Crawl4AI's LLM extraction capabilities to intelligently
discover PDF documents from investor relations websites, handling JavaScript-
rendered content and complex page structures.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

import asyncio
import logging
from typing import Any
from urllib.parse import urljoin, urlparse

from crawl4ai import AsyncWebCrawler, LLMConfig
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class DiscoveredPDF(BaseModel):
    """Represents a discovered PDF document with metadata."""

    url: str
    filename: str
    fiscal_year: int | None = None
    document_type: str = "unknown"
    title: str | None = None
    description: str | None = None
    confidence: float = 1.0


class ScrapingService:
    """Service for scraping investor relations websites using Crawl4AI."""

    def __init__(self, openai_api_key: str | None = None):
        """
        Initialize the scraping service.

        Args:
            openai_api_key: Optional OpenAI API key for LLM extraction.
                If not provided, will fall back to CSS/XPath extraction.
        """
        self.openai_api_key = openai_api_key
        self._crawler: AsyncWebCrawler | None = None

    async def __aenter__(self):
        """Async context manager entry."""
        await self._initialize_crawler()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self._cleanup()

    async def _initialize_crawler(self) -> None:
        """Initialize the Crawl4AI crawler with appropriate configuration."""
        if self._crawler is None:
            # Configure crawler for polite scraping
            self._crawler = AsyncWebCrawler(
                headless=True,  # Use headless browser
                browser_type="chromium",  # Use Chromium
                verbose=False,  # Reduce verbose output
                # Respect robots.txt and add delays
                wait_for_images=False,  # Don't wait for images (faster)
                screenshot=False,  # Don't capture screenshots
            )

    async def _cleanup(self) -> None:
        """Clean up crawler resources."""
        if self._crawler is not None:
            await self._crawler.close()
            self._crawler = None

    async def discover_pdf_urls(self, ir_url: str, use_llm: bool = True) -> list[DiscoveredPDF]:
        """
        Discover PDF URLs from an investor relations website.

        Uses Crawl4AI with LLM extraction to intelligently find PDF links
        even in complex, JavaScript-rendered pages.

        Args:
            ir_url: Investor relations website URL.
            use_llm: Whether to use LLM extraction (requires OpenAI API key).
                If False, falls back to CSS/XPath extraction.

        Returns:
            List of discovered PDF documents with metadata.

        Raises:
            ValueError: If crawler initialization fails.
            Exception: If scraping fails.
        """
        await self._initialize_crawler()

        if self._crawler is None:
            raise ValueError("Crawler not initialized")

        # Add polite delay before scraping
        await asyncio.sleep(1.0)

        logger.info(
            f"Discovering PDFs from {ir_url} using {'LLM' if use_llm else 'CSS/XPath'} extraction"
        )

        try:
            if use_llm and self.openai_api_key:
                # Use LLM extraction strategy for intelligent PDF discovery
                pdfs = await self._discover_with_llm(ir_url)
            else:
                # Fallback to CSS/XPath extraction
                pdfs = await self._discover_with_css(ir_url)

            logger.info(f"Discovered {len(pdfs)} PDF documents from {ir_url}")
            return pdfs

        except Exception as e:
            logger.error(
                f"Failed to discover PDFs from {ir_url}: {e}",
                exc_info=True,
                extra={"url": ir_url},
            )
            raise

    async def _discover_with_llm(self, ir_url: str) -> list[DiscoveredPDF]:
        """
        Discover PDFs using LLM extraction strategy.

        Uses Crawl4AI's LLM extraction to intelligently find and extract
        information about PDF documents, including metadata like fiscal year
        and document type.

        Args:
            ir_url: Investor relations website URL.

        Returns:
            List of discovered PDF documents.
        """
        if not self.openai_api_key:
            logger.warning("OpenAI API key not available, falling back to CSS extraction")
            return await self._discover_with_css(ir_url)

        # Define extraction schema for LLM
        extraction_schema = {
            "type": "object",
            "properties": {
                "pdfs": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "Full URL of the PDF document",
                            },
                            "title": {
                                "type": "string",
                                "description": "Title or name of the document (e.g., 'Annual Report 2024')",
                            },
                            "fiscal_year": {
                                "type": "integer",
                                "description": "Fiscal year if identifiable from title or context (e.g., 2024)",
                            },
                            "document_type": {
                                "type": "string",
                                "enum": [
                                    "annual_report",
                                    "quarterly_report",
                                    "investor_presentation",
                                    "prospectus",
                                    "other",
                                    "unknown",
                                ],
                                "description": "Type of financial document",
                            },
                            "description": {
                                "type": "string",
                                "description": "Brief description or context from surrounding text",
                            },
                        },
                        "required": ["url", "title"],
                    },
                }
            },
            "required": ["pdfs"],
        }

        # Create LLM extraction strategy
        try:
            # Create LLM config with API token
            llm_config = LLMConfig(api_token=self.openai_api_key)

            extraction_strategy = LLMExtractionStrategy(
                llm_config=llm_config,
                schema=extraction_schema,
                extraction_type="schema",
                instruction=(
                    "Extract all PDF document links from this investor relations page. "
                    "Focus on annual reports, quarterly reports, and financial statements. "
                    "Identify the fiscal year from document titles (e.g., 'Annual Report 2024' → fiscal_year: 2024). "
                    "Classify documents by type based on title and context. "
                    "Include both direct PDF links and links to pages that contain PDF downloads. "
                    "Resolve relative URLs to absolute URLs."
                ),
            )
        except Exception as e:
            logger.warning(
                f"Failed to create LLM extraction strategy: {e}, falling back to CSS extraction",
                exc_info=True,
            )
            return await self._discover_with_css(ir_url)

        # Run crawler with LLM extraction
        try:
            result = await self._crawler.arun(
                url=ir_url,
                extraction_strategy=extraction_strategy,
                wait_for="domcontentloaded",  # Wait for DOM to load
                delay_before_return_html=2.0,  # Wait 2 seconds for JS to render
            )
        except Exception as e:
            logger.error(
                f"Error during Crawl4AI LLM extraction for {ir_url}: {e}",
                exc_info=True,
                extra={"url": ir_url},
            )
            # Fallback to CSS extraction on error
            return await self._discover_with_css(ir_url)

        if result.success:
            # Parse LLM extraction results
            return self._parse_llm_results(result, ir_url)
        else:
            logger.warning(
                f"LLM extraction failed for {ir_url}, falling back to CSS extraction",
                extra={"url": ir_url, "error": result.error_message},
            )
            return await self._discover_with_css(ir_url)

    async def _discover_with_css(self, ir_url: str) -> list[DiscoveredPDF]:
        """
        Discover PDFs using CSS/XPath extraction (fallback method).

        Uses traditional CSS selectors to find PDF links. Less intelligent
        than LLM extraction but doesn't require API key.

        Args:
            ir_url: Investor relations website URL.

        Returns:
            List of discovered PDF documents.
        """
        # Run crawler to get page content
        try:
            result = await self._crawler.arun(
                url=ir_url,
                wait_for="domcontentloaded",
                delay_before_return_html=2.0,
            )

            if not result.success:
                logger.error(
                    f"Failed to crawl {ir_url}: {result.error_message}",
                    extra={"url": ir_url, "error": result.error_message},
                )
                return []
        except Exception as e:
            logger.error(
                f"Exception during CSS-based crawling for {ir_url}: {e}",
                exc_info=True,
                extra={"url": ir_url},
            )
            return []

        # Extract PDF links using CSS selectors
        pdfs: list[DiscoveredPDF] = []

        # Parse markdown or HTML content to find PDF links
        content = result.markdown or result.html or ""

        # Use BeautifulSoup from markdown/HTML content
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(content, "lxml")

        # Find all links that point to PDFs
        for link in soup.find_all("a", href=True):
            href = link.get("href", "")
            link_text = link.get_text(strip=True)

            # Check if link points to PDF
            if href.lower().endswith(".pdf") or ".pdf" in href.lower():
                # Resolve relative URLs
                pdf_url = urljoin(ir_url, href)

                # Try to extract metadata from link text
                fiscal_year = self._extract_fiscal_year(link_text)
                doc_type = self._classify_document_type(link_text, href)

                pdfs.append(
                    DiscoveredPDF(
                        url=pdf_url,
                        filename=self._extract_filename(pdf_url),
                        fiscal_year=fiscal_year,
                        document_type=doc_type,
                        title=link_text or None,
                        confidence=0.8,  # Lower confidence for CSS extraction
                    )
                )

        # Deduplicate by URL
        seen_urls = set()
        unique_pdfs = []
        for pdf in pdfs:
            if pdf.url not in seen_urls:
                seen_urls.add(pdf.url)
                unique_pdfs.append(pdf)

        return unique_pdfs

    def _parse_llm_results(self, result: Any, base_url: str) -> list[DiscoveredPDF]:
        """
        Parse LLM extraction results into DiscoveredPDF objects.

        Args:
            result: Crawl4AI result object with LLM extraction data.
            base_url: Base URL for resolving relative URLs.

        Returns:
            List of discovered PDF documents.
        """
        pdfs: list[DiscoveredPDF] = []

        try:
            # Extract JSON from LLM result
            extracted_content = result.extracted_content

            if not extracted_content:
                logger.warning("No extracted content from LLM")
                return []

            # Parse JSON response
            import json

            if isinstance(extracted_content, str):
                data = json.loads(extracted_content)
            else:
                data = extracted_content

            # Extract PDFs array
            pdfs_data = data.get("pdfs", [])

            for pdf_data in pdfs_data:
                url = pdf_data.get("url", "")
                if not url:
                    continue

                # Resolve relative URLs
                if not url.startswith(("http://", "https://")):
                    url = urljoin(base_url, url)

                # Extract metadata
                fiscal_year = pdf_data.get("fiscal_year")
                doc_type = pdf_data.get("document_type", "unknown")
                title = pdf_data.get("title", "")
                description = pdf_data.get("description")

                pdfs.append(
                    DiscoveredPDF(
                        url=url,
                        filename=self._extract_filename(url),
                        fiscal_year=fiscal_year,
                        document_type=doc_type,
                        title=title,
                        description=description,
                        confidence=0.95,  # High confidence for LLM extraction
                    )
                )

        except Exception as e:
            logger.error(
                f"Failed to parse LLM results: {e}",
                exc_info=True,
                extra={"base_url": base_url},
            )

        return pdfs

    def _extract_fiscal_year(self, text: str) -> int | None:
        """
        Extract fiscal year from text using pattern matching.

        Args:
            text: Text to search for year.

        Returns:
            Fiscal year if found, None otherwise.
        """
        import re

        # Look for 4-digit years (2000-2099)
        year_pattern = r"\b(20\d{2})\b"
        matches = re.findall(year_pattern, text)

        if matches:
            # Return the most recent year found
            years = [int(y) for y in matches]
            return max(years)

        return None

    def _classify_document_type(self, text: str, url: str) -> str:
        """
        Classify document type based on text and URL patterns.

        Args:
            text: Link text or title.
            url: Document URL.

        Returns:
            Document type classification.
        """
        text_lower = text.lower()
        url_lower = url.lower()

        # Check for annual report indicators
        if any(
            keyword in text_lower or keyword in url_lower
            for keyword in ["annual", "ar ", "year-end"]
        ):
            return "annual_report"

        # Check for quarterly report indicators
        if any(
            keyword in text_lower or keyword in url_lower
            for keyword in ["quarterly", "q1", "q2", "q3", "q4", "quarter"]
        ):
            return "quarterly_report"

        # Check for investor presentation
        if any(
            keyword in text_lower or keyword in url_lower
            for keyword in ["presentation", "investor", "deck"]
        ):
            return "investor_presentation"

        # Check for prospectus
        if "prospectus" in text_lower or "prospectus" in url_lower:
            return "prospectus"

        return "unknown"

    def _extract_filename(self, url: str) -> str:
        """
        Extract filename from URL.

        Args:
            url: PDF URL.

        Returns:
            Filename extracted from URL.
        """
        parsed = urlparse(url)
        filename = parsed.path.split("/")[-1]

        if not filename or not filename.endswith(".pdf"):
            # Generate a default filename
            filename = "document.pdf"

        return filename
