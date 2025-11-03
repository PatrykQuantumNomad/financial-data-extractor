"""
Scraping service using Crawl4AI for intelligent PDF discovery.

This service uses Crawl4AI's LLM extraction capabilities to intelligently
discover PDF documents from investor relations websites, handling JavaScript-
rendered content and complex page structures.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

import asyncio
import json
import logging
import re
from typing import Any
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup
from crawl4ai import AsyncWebCrawler, BrowserConfig, CacheMode, CrawlerRunConfig, LLMConfig
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class PDFLink(BaseModel):
    title: str = Field(..., description="Title, description, or text associated with this PDF")
    primary_url: str = Field(
        ..., description="Main URL (could be article/document page or direct PDF)"
    )
    download_url: str | None = Field(
        None, description="Separate download URL if different from primary_url"
    )
    link_text: str | None = Field(
        None,
        description="Text of the link or button (e.g., 'Download PDF', '[PDF]', 'Annual Report')",
    )
    context: str | None = Field(
        None, description="Surrounding text or context that helps identify the document"
    )
    year: int | None = Field(None, description="Year if mentioned in title, URL, or context")
    document_type: str | None = Field(
        None,
        description="Type: annual_report, quarterly_report, presentation, academic_paper, or other",
    )
    pdf_indicator: str = Field(
        ...,
        description="How PDF was identified: direct_link, download_button, pdf_badge, viewer_page, or embedded",
    )


class PDFCollection(BaseModel):
    """Collection of discovered PDF documents."""

    pdfs: list[PDFLink] = Field(default=[], description="All PDFs and PDF-related links found")


class DiscoveredPDF(BaseModel):
    """Represents a discovered PDF document with metadata (legacy format for compatibility)."""

    url: str
    filename: str
    fiscal_year: int | None = None
    document_type: str = "unknown"
    title: str | None = None
    description: str | None = None
    confidence: float = 1.0


class ScrapingService:
    """Service for scraping investor relations websites using Crawl4AI."""

    def __init__(
        self,
        openrouter_api_key: str | None = None,
        openrouter_model: str | None = None,
        max_crawl_depth: int = 2,
    ):
        """
        Initialize the scraping service.

        Args:
            openrouter_api_key: Optional OpenRouter API key for LLM extraction.
            openrouter_model: Optional OpenRouter model to use (defaults to config value).
            max_crawl_depth: Maximum depth for deep crawling (default: 2).
        """
        self.openrouter_api_key = openrouter_api_key

        # Get model from config if not provided
        if openrouter_model is None:
            from config import Settings

            settings = Settings()
            openrouter_model = settings.open_router_model_scraping

        self.openrouter_model = openrouter_model
        self.max_crawl_depth = max_crawl_depth
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
            # Configure browser for polite scraping
            browser_config = BrowserConfig(
                headless=True,
                viewport_width=1920,
                viewport_height=1080,
                browser_type="chromium",
            )

            self._crawler = AsyncWebCrawler(config=browser_config)
            await self._crawler.start()

    async def _cleanup(self) -> None:
        """Clean up crawler resources."""
        if self._crawler is not None:
            await self._crawler.close()
            self._crawler = None

    async def discover_pdf_urls(self, ir_url: str, use_llm: bool = True) -> list[DiscoveredPDF]:
        """
        Discover PDF URLs from an investor relations website using deep crawling.

        Uses Crawl4AI with LLM extraction to intelligently find PDF links
        even in complex, JavaScript-rendered pages. Performs deep crawling
        across multiple pages to discover PDFs in nested sections.

        Args:
            ir_url: Investor relations website URL.
            use_llm: Whether to use LLM extraction (requires OpenRouter API key).

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
            f"Discovering PDFs from {ir_url} using {'LLM' if use_llm else 'CSS'} extraction"
        )

        try:
            if use_llm and self.openrouter_api_key:
                # Use deep crawling with LLM extraction
                pdfs = await self._deep_crawl_with_llm(ir_url)
            else:
                # Fallback to CSS/XPath extraction
                pdfs = await self._discover_with_css(ir_url)

            # Deduplicate by URL
            seen_urls = set()
            unique_pdfs = []
            for pdf in pdfs:
                if pdf.url not in seen_urls:
                    seen_urls.add(pdf.url)
                    unique_pdfs.append(pdf)

            logger.info(f"Discovered {len(unique_pdfs)} unique PDF documents from {ir_url}")
            return unique_pdfs

        except Exception as e:
            logger.error(
                f"Failed to discover PDFs from {ir_url}: {e}",
                exc_info=True,
                extra={"url": ir_url},
            )
            raise

    async def _deep_crawl_with_llm(self, ir_url: str) -> list[DiscoveredPDF]:
        """
        Discover PDFs using deep crawling with LLM extraction.

        Strategy:
        1. Crawl main IR page
        2. Extract links to financial sections (Annual Reports, etc.)
        3. Crawl discovered pages in parallel
        4. Extract PDFs from all results with LLM

        Args:
            ir_url: Investor relations website URL.

        Returns:
            List of discovered PDF documents.
        """
        if not self.openrouter_api_key:
            logger.warning("OpenRouter API key not available, falling back to CSS extraction")
            return await self._discover_with_css(ir_url)

        # Configure crawler for deep crawling
        # Use wait_until for page load states, wait_for is for CSS/JS selectors
        crawler_config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,  # Fresh data
            wait_until="domcontentloaded",  # Wait for DOM to be ready (faster than networkidle)
            wait_for_timeout=30000,  # 30 second timeout for wait condition
            page_timeout=90000,  # 90 second overall page timeout
            screenshot=False,
            pdf=False,
            verbose=False,
        )

        # Step 1: Crawl main IR page to find financial section links
        logger.info(f"Step 1: Crawling main IR page: {ir_url}")
        try:
            main_result = await self._crawler.arun(url=ir_url, config=crawler_config)
        except Exception as e:
            logger.warning(
                f"Error crawling main page with load condition: {e}, trying with shorter timeout",
                exc_info=True,
            )
            # Try with even more lenient settings
            crawler_config = CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,
                wait_until="domcontentloaded",  # Most lenient - just wait for DOM
                wait_for_timeout=15000,  # 15 seconds
                page_timeout=60000,  # 60 seconds
                screenshot=False,
                pdf=False,
                verbose=False,
            )
            try:
                main_result = await self._crawler.arun(url=ir_url, config=crawler_config)
            except Exception as e2:
                logger.error(
                    f"Failed to crawl main page even with lenient settings: {e2}",
                    exc_info=True,
                )
                # Try LLM extraction on partial HTML if we can get it via direct HTTP
                # This allows LLM to work even when browser crawl fails
                try:
                    pdfs = await self._try_llm_extraction_on_http_content(ir_url)
                    if pdfs:
                        logger.info(
                            f"Successfully extracted {len(pdfs)} PDFs using LLM on HTTP content"
                        )
                        return pdfs
                except Exception as e3:
                    logger.warning(
                        f"LLM extraction on HTTP content also failed: {e3}, falling back to CSS extraction",
                        exc_info=True,
                    )
                # Fallback to CSS extraction which might work with partial content
                return await self._discover_with_css(ir_url)

        if not main_result.success:
            logger.warning("Failed to crawl main page, falling back to CSS extraction")
            return await self._discover_with_css(ir_url)

        # Step 2: Extract links to financial sections
        section_links = self._extract_financial_section_links(main_result, ir_url)
        logger.info(f"Found {len(section_links)} financial section links")

        # Step 3: Prepare URLs to crawl (main page + top sections, limit to reasonable number)
        urls_to_crawl = [ir_url] + section_links[: min(5, self.max_crawl_depth)]
        logger.info(f"Step 2: Deep crawling {len(urls_to_crawl)} pages")

        # Step 4: Crawl all URLs in parallel with lenient wait conditions
        # Use same config as main page (already lenient)
        try:
            results = await self._crawler.arun_many(urls=urls_to_crawl, config=crawler_config)
        except Exception as e:
            logger.warning(
                f"Error during parallel crawl: {e}, falling back to individual crawling",
                exc_info=True,
            )
            # Fallback: crawl individually with more lenient settings
            crawler_config = CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,
                wait_until="domcontentloaded",
                wait_for_timeout=15000,
                page_timeout=60000,
                screenshot=False,
                pdf=False,
                verbose=False,
            )
            results = []
            for url in urls_to_crawl:
                try:
                    result = await self._crawler.arun(url=url, config=crawler_config)
                    if result:
                        results.append(result)
                except Exception as e2:
                    logger.warning(f"Failed to crawl {url}: {e2}")

        # Step 5: Extract PDFs from all crawled results using LLM
        all_pdfs: list[DiscoveredPDF] = []

        for i, result in enumerate(results):
            if not result.success:
                logger.warning(f"Failed to crawl URL {i}: {result.error_message}")
                continue

            # Extract PDFs with LLM
            pdfs = await self._extract_pdfs_with_llm_from_page(result, ir_url)
            all_pdfs.extend(pdfs)
            logger.info(f"Extracted {len(pdfs)} PDFs from page {i + 1}/{len(results)}")

        return all_pdfs

    def _extract_financial_section_links(self, result: Any, base_url: str) -> list[str]:
        """
        Extract links to financial sections (Annual Reports, etc.) from main page.

        Uses simple pattern matching to find relevant section links.

        Args:
            result: Crawl4AI result object.
            base_url: Base URL for resolving relative URLs.

        Returns:
            List of section URLs.
        """
        if not result.success:
            return []

        # Parse HTML to find financial section links
        html = result.html or ""
        soup = BeautifulSoup(html, "lxml")

        # Keywords that indicate financial sections
        keywords = [
            "annual report",
            "annual reports",
            "quarterly report",
            "financial report",
            "financial reports",
            "investor relations",
            "financial statements",
            "earnings",
            "investor center",
            "financial information",
            "results & presentations",
        ]

        section_urls = []
        seen_urls = {base_url}

        for link in soup.find_all("a", href=True):
            href = link.get("href", "")
            link_text = link.get_text(strip=True).lower()

            # Check if link text contains financial keywords
            if any(keyword in link_text for keyword in keywords):
                # Resolve relative URLs
                full_url = urljoin(base_url, href)
                url_str = str(full_url)

                # Avoid duplicates and external links
                if url_str not in seen_urls and url_str.startswith(base_url):
                    section_urls.append(url_str)
                    seen_urls.add(url_str)

        # Limit to reasonable number of sections
        return section_urls[:10]

    async def _extract_pdfs_with_llm_from_page(
        self, result: Any, base_url: str
    ) -> list[DiscoveredPDF]:
        """
        Extract PDFs from a single page using LLM extraction with Pydantic schema.

        Uses the PDFCollection Pydantic model for structured extraction, following
        the pattern from Crawl4AI examples.

        Args:
            result: Crawl4AI result object.
            base_url: Base URL for resolving relative URLs.

        Returns:
            List of discovered PDF documents.
        """
        if not result.success:
            return []

        try:
            # Set temperature=1 only for GPT-5 models, otherwise omit or allow configurable
            use_gpt5 = self.openrouter_model and "gpt-5" in self.openrouter_model.lower()

            llm_config = LLMConfig(
                provider=self.openrouter_model,
                api_token=self.openrouter_api_key,
                base_url="https://openrouter.ai/api/v1",
            )

            # Use Pydantic model's JSON schema directly
            from app.core.llm.prompts import PDF_DISCOVERY_INSTRUCTION

            extraction_strategy = LLMExtractionStrategy(
                llm_config=llm_config,
                schema=PDFCollection.model_json_schema(),
                extraction_type="schema",
                instruction=PDF_DISCOVERY_INSTRUCTION,
                extra_args={"temperature": 1} if use_gpt5 else None,
            )

            # Re-run crawler with LLM extraction on the same page
            # Use lenient wait conditions to avoid timeouts
            crawler_config = CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,
                wait_until="domcontentloaded",  # More reliable than networkidle
                wait_for_timeout=30000,  # 30 seconds
                page_timeout=90000,  # 90 seconds
                screenshot=False,
                pdf=False,
                verbose=False,
                extraction_strategy=extraction_strategy,
            )

            llm_result = await self._crawler.arun(url=result.url, config=crawler_config)

            # Check the whole llm_result content and log for debugging if extraction failed
            if llm_result.success:
                # Log info about llm_result for diagnostics of missing extracted_content
                if not llm_result.extracted_content:
                    logger.warning(
                        f"LLM ran successfully but produced no extracted_content for {result.url}: {llm_result}",
                        extra={"llm_result": repr(llm_result)},
                    )
                else:
                    return self._parse_llm_results(llm_result, base_url)
        except Exception as e:
            logger.warning(
                f"LLM extraction failed for page: {e}, falling back to simple regex extraction",
                exc_info=True,
            )

        # Fallback to simple regex-based extraction if LLM fails
        return await self._discover_with_regex(result, base_url)

    async def _discover_with_regex(self, result: Any, base_url: str) -> list[DiscoveredPDF]:
        """
        Discover PDFs using simple regex pattern matching (no LLM required).

        Faster and cheaper alternative to LLM extraction. Searches for PDF links
        in HTML content using regex patterns.

        Args:
            result: Crawl4AI result object.
            base_url: Base URL for resolving relative URLs.

        Returns:
            List of discovered PDF documents.
        """
        if not result.success:
            return []

        pdfs: list[DiscoveredPDF] = []
        seen_urls = set()

        try:
            # Extract all links from the page
            internal_links = result.links.get("internal", []) if hasattr(result, "links") else []
            external_links = result.links.get("external", []) if hasattr(result, "links") else []
            all_links = internal_links + external_links

            # Extract URLs from links (they might be strings or dicts with 'url' key)
            def extract_url(link: str | dict) -> str:
                """Extract URL from link, handling both string and dict formats."""
                if isinstance(link, str):
                    return link
                elif isinstance(link, dict):
                    # crawl4ai may return dict with 'url', 'href', or other keys
                    return link.get("url") or link.get("href") or str(link)
                else:
                    return str(link)

            # Convert all links to URL strings
            all_link_urls = [extract_url(link) for link in all_links if extract_url(link)]

            # Filter for PDF links
            pdf_links = [
                link_url
                for link_url in all_link_urls
                if link_url and link_url.lower().endswith(".pdf")
            ]

            # Also search in the HTML content for PDF references
            html_content = result.html or ""
            pdf_pattern = r'href=["\']([^"\']*\.pdf[^"\']*)["\']'
            pdf_matches = re.findall(pdf_pattern, html_content, re.IGNORECASE)

            # Combine and deduplicate
            all_pdf_urls = list(set(pdf_links + pdf_matches))

            for pdf_url in all_pdf_urls:
                if pdf_url in seen_urls:
                    continue

                # Resolve relative URLs
                if not pdf_url.startswith(("http://", "https://")):
                    pdf_url = urljoin(base_url, pdf_url)

                seen_urls.add(pdf_url)

                # Try to extract metadata from URL with fallback to filename
                fiscal_year = self._extract_fiscal_year(pdf_url)
                # If extraction failed, try extracting from filename part of URL
                if fiscal_year is None:
                    parsed = urlparse(pdf_url)
                    filename = parsed.path.split("/")[-1]
                    fiscal_year = self._extract_fiscal_year(filename)
                doc_type = self._classify_document_type(pdf_url, pdf_url)

                pdfs.append(
                    DiscoveredPDF(
                        url=pdf_url,
                        filename=self._extract_filename(pdf_url),
                        fiscal_year=fiscal_year,
                        document_type=doc_type,
                        title=None,
                        description=None,
                        confidence=0.7,  # Lower confidence for regex extraction
                    )
                )

            logger.info(f"Found {len(pdfs)} PDF(s) using regex extraction")

        except Exception as e:
            logger.error(
                f"Error during regex-based PDF discovery: {e}",
                exc_info=True,
                extra={"base_url": base_url},
            )

        return pdfs

    async def _try_llm_extraction_on_http_content(self, ir_url: str) -> list[DiscoveredPDF]:
        """
        Try LLM extraction using direct HTTP fetch when browser crawl fails.

        This allows LLM extraction to work even when Crawl4AI browser automation fails.
        We fetch the HTML directly via HTTP and pass it to LLM for extraction.

        Args:
            ir_url: Investor relations website URL.

        Returns:
            List of discovered PDF documents, or empty list if extraction fails.
        """
        if not self.openrouter_api_key:
            return []

        logger.info(f"Attempting LLM extraction on HTTP content for {ir_url}")

        try:
            # Fetch HTML content directly via HTTP
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }

            async with httpx.AsyncClient(
                timeout=httpx.Timeout(30.0, connect=10.0),
                headers=headers,
                follow_redirects=True,
            ) as client:
                # Verify we can fetch the URL
                response = await client.get(ir_url)
                response.raise_for_status()

            # If crawler is available, try with a minimal config - just fetch and extract
            if self._crawler:
                try:
                    minimal_config = CrawlerRunConfig(
                        cache_mode=CacheMode.BYPASS,
                        wait_until=None,
                        delay_before_return_html=0.5,
                        page_timeout=30000,
                        screenshot=False,
                        pdf=False,
                        verbose=False,
                    )
                    # Use HTTP mode if available, otherwise try minimal browser
                    result = await self._crawler.arun(url=ir_url, config=minimal_config)
                    if result and result.html:
                        # Now run LLM extraction on this result
                        pdfs = await self._extract_pdfs_with_llm_from_page(result, ir_url)
                        return pdfs
                except Exception as e:
                    logger.warning(f"Failed to run minimal crawl for LLM: {e}")

            # If all else fails, fall back to regex extraction with the HTTP content
            logger.warning(
                "Could not use LLM extraction on HTTP content, this is expected if browser is required"
            )
            return []

        except Exception as e:
            logger.error(
                f"Failed to extract PDFs using LLM on HTTP content: {e}",
                exc_info=True,
            )
            return []

    def _parse_llm_results(self, result: Any, base_url: str) -> list[DiscoveredPDF]:
        """
        Parse LLM extraction results into DiscoveredPDF objects.

        Uses the PDFCollection Pydantic model for type-safe parsing.

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
                logger.debug("No extracted content from LLM")
                return []

            # Parse JSON response
            if isinstance(extracted_content, str):
                data = json.loads(extracted_content)
            else:
                data = extracted_content

            # Handle case where LLM returns array directly instead of {"pdfs": [...]}
            if isinstance(data, list):
                data = {"pdfs": data}
            elif not isinstance(data, dict):
                logger.warning(f"Unexpected LLM response format: {type(data)}")
                return []

            # Filter out extra fields that aren't in PDFInfo model (e.g., pdf_type, error)
            # and ensure all required fields are present
            cleaned_pdfs = []
            for pdf_item in data.get("pdfs", []):
                if not isinstance(pdf_item, dict):
                    continue

                # Extract only fields that PDFInfo expects, with defaults
                cleaned_pdf = {
                    "title": pdf_item.get("title", ""),
                    "primary_url": pdf_item.get("primary_url", ""),
                    "download_url": pdf_item.get("download_url", ""),
                    "link_text": pdf_item.get("link_text", ""),
                    "context": pdf_item.get("context", ""),
                    "year": pdf_item.get("year"),
                    "document_type": pdf_item.get("document_type", "unknown"),
                    "pdf_indicator": pdf_item.get("pdf_indicator", "unknown"),
                }

                cleaned_pdfs.append(cleaned_pdf)

            # Validate with Pydantic model
            try:
                pdf_collection = PDFCollection(pdfs=cleaned_pdfs)
            except Exception as e:
                logger.warning(
                    f"Failed to validate LLM response with Pydantic model: {e}",
                    exc_info=True,
                )
                # Last resort: try to parse individual items
                pdf_collection = PDFCollection(pdfs=[])
                for pdf_item in cleaned_pdfs:
                    try:
                        pdf_link = PDFLink(**pdf_item)
                        pdf_collection.pdfs.append(pdf_link)
                    except Exception as item_error:
                        logger.debug(f"Skipping invalid PDF item: {item_error}")

            # Convert PDFInfo to DiscoveredPDF
            for pdf_link in pdf_collection.pdfs:
                # Resolve relative URLs
                url = pdf_link.download_url
                if not url:
                    url = pdf_link.primary_url

                if not url.startswith(("http://", "https://")):
                    url = urljoin(base_url, url)

                # Normalize empty strings to None for optional fields
                # Handle None, empty strings, and whitespace-only strings
                title = (pdf_link.title or "").strip() or None
                description = (pdf_link.document_type or "").strip() or None

                pdfs.append(
                    DiscoveredPDF(
                        url=url,
                        filename=self._extract_filename(url),
                        fiscal_year=pdf_link.year,
                        document_type=pdf_link.document_type or "unknown",
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
        # Configure crawler for simple crawling
        # Use lenient wait conditions to handle sites with continuous network activity
        crawler_config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,  # Fresh data
            wait_until="domcontentloaded",  # Wait for DOM ready instead of networkidle
            wait_for_timeout=30000,  # 30 second timeout for wait condition
            page_timeout=90000,  # 90 second overall timeout
            screenshot=False,
            pdf=False,
            verbose=False,
        )

        # Crawl main page with progressive fallback strategy
        result = None
        try:
            result = await self._crawler.arun(url=ir_url, config=crawler_config)
        except Exception as e:
            logger.warning(
                f"Failed with 'domcontentloaded' condition: {e}, trying with no wait condition",
                exc_info=True,
            )
            # Try with even more lenient settings - no wait, just delay
            crawler_config = CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,
                wait_until=None,  # No wait condition, use delay instead
                delay_before_return_html=3.0,  # Wait 3 seconds before capture
                wait_for_timeout=15000,  # 15 seconds
                page_timeout=60000,  # 60 seconds
                screenshot=False,
                pdf=False,
                verbose=False,
            )
            try:
                result = await self._crawler.arun(url=ir_url, config=crawler_config)
            except Exception as e2:
                logger.error(
                    f"Failed to crawl even with lenient settings: {e2}, attempting regex extraction without full page load",
                    exc_info=True,
                )
                # Last resort: try to get partial content
                return await self._try_regex_extraction_without_crawl(ir_url)

        if not result or not result.success:
            logger.error(
                f"Failed to crawl {ir_url}: {result.error_message if result else 'No result'}",
            )
            # Try regex extraction as last resort
            return await self._try_regex_extraction_without_crawl(ir_url)

        return self._discover_with_css_from_result(result, ir_url)

    async def _try_regex_extraction_without_crawl(self, ir_url: str) -> list[DiscoveredPDF]:
        """
        Last resort: Try to extract PDFs using direct HTTP request and regex.

        Used when Crawl4AI fails completely. Makes a simple HTTP GET request
        and uses regex to find PDF links in the HTML.

        Args:
            ir_url: Investor relations website URL.

        Returns:
            List of discovered PDF documents.
        """
        logger.info(f"Attempting direct HTTP fetch for {ir_url} as last resort")
        pdfs: list[DiscoveredPDF] = []

        try:
            # Make a simple HTTP request with polite headers (httpx imported at module level)
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }

            async with httpx.AsyncClient(
                timeout=httpx.Timeout(30.0, connect=10.0),
                headers=headers,
                follow_redirects=True,
            ) as client:
                response = await client.get(ir_url)
                response.raise_for_status()
                html_content = response.text

                # Use regex to find PDF links
                pdf_pattern = r'href=["\']([^"\']*\.pdf[^"\']*)["\']'
                pdf_matches = re.findall(pdf_pattern, html_content, re.IGNORECASE)

                # Also look for links in anchor tags using BeautifulSoup
                soup = BeautifulSoup(html_content, "lxml")
                for link in soup.find_all("a", href=True):
                    href = link.get("href", "")
                    if href.lower().endswith(".pdf") or ".pdf" in href.lower():
                        if href not in pdf_matches:
                            pdf_matches.append(href)

                # Deduplicate and create DiscoveredPDF objects
                seen_urls = set()
                for pdf_url in pdf_matches:
                    if pdf_url in seen_urls:
                        continue

                    # Resolve relative URLs
                    if not pdf_url.startswith(("http://", "https://")):
                        pdf_url = urljoin(ir_url, pdf_url)

                    seen_urls.add(pdf_url)

                    # Try to extract metadata - extract from URL with better pattern matching
                    fiscal_year = self._extract_fiscal_year(pdf_url)
                    # If extraction failed, try extracting from filename part of URL
                    if fiscal_year is None:
                        # Extract just the filename from URL and try again
                        parsed = urlparse(pdf_url)
                        filename = parsed.path.split("/")[-1]
                        fiscal_year = self._extract_fiscal_year(filename)

                    doc_type = self._classify_document_type(pdf_url, pdf_url)

                    pdfs.append(
                        DiscoveredPDF(
                            url=pdf_url,
                            filename=self._extract_filename(pdf_url),
                            fiscal_year=fiscal_year,
                            document_type=doc_type,
                            title=None,
                            description=None,
                            confidence=0.6,  # Lower confidence for simple HTTP extraction
                        )
                    )

                logger.info(f"Found {len(pdfs)} PDF(s) using direct HTTP + regex extraction")

        except Exception as e:
            logger.error(
                f"Failed to extract PDFs using direct HTTP: {e}",
                exc_info=True,
                extra={"url": ir_url},
            )

        return pdfs

    def _discover_with_css_from_result(self, result: Any, base_url: str) -> list[DiscoveredPDF]:
        """
        Extract PDFs from a crawled result using CSS selectors.

        Args:
            result: Crawl4AI result object.
            base_url: Base URL for resolving relative URLs.

        Returns:
            List of discovered PDF documents.
        """
        if not result.success:
            return []

        # Parse markdown or HTML content to find PDF links
        content = result.markdown or result.html or ""
        soup = BeautifulSoup(content, "lxml")

        pdfs: list[DiscoveredPDF] = []

        # Find all links that point to PDFs
        for link in soup.find_all("a", href=True):
            href = link.get("href", "")
            link_text = link.get_text(strip=True)

            # Check if link points to PDF
            if href.lower().endswith(".pdf") or ".pdf" in href.lower():
                # Resolve relative URLs
                pdf_url = urljoin(base_url, href)

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

        return pdfs

    def _extract_fiscal_year(self, text: str) -> int | None:
        """
        Extract fiscal year from text using pattern matching.

        Handles various formats like:
        - "AstraZeneca_AR_2017 (1).pdf" -> 2017
        - "annual-report-2024.pdf" -> 2024
        - "2023_Annual_Report" -> 2023

        Args:
            text: Text to search for year.

        Returns:
            Fiscal year if found, None otherwise.
        """
        if not text:
            return None

        # Look for 4-digit years (2000-2099) - improved pattern
        # Matches years even with special characters like parentheses
        year_pattern = r"(?:^|[^0-9])(20[0-2][0-9])(?:[^0-9]|$)"
        matches = re.findall(year_pattern, text)

        if matches:
            # Return the most recent year found (typically the fiscal year)
            years = [int(y) for y in matches]
            # Filter to reasonable range (2000-2099, with practical limits)
            years = [y for y in years if 2000 <= y <= 2099]
            if years:
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
