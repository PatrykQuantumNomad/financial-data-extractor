"""
Integration tests for scraping service.

Tests PDF discovery from websites without downloading PDFs.
Tests are designed to be fast and focused on discovery logic.

These tests don't require database or testcontainers - they only test web scraping.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

import pytest

from app.core.scraping import ScrapingService

# Use scraping-specific fixtures (no database required)
# This prevents loading the main conftest's database fixtures
pytest_plugins = []


@pytest.mark.asyncio
@pytest.mark.integration
async def test_discover_pdfs_simple_website():
    """Test PDF discovery from a simple website that should work with basic crawling."""
    test_url = "https://scholar.google.ca/scholar?hl=en&as_sdt=0%2C5&q=ai&btnG="

    async with ScrapingService() as service:
        # Test without LLM (should use CSS/regex extraction)
        pdfs = await service.discover_pdf_urls(test_url, use_llm=False)

        # Assert that we get a result (even if empty)
        assert isinstance(pdfs, list)
        # The service should not crash even if no PDFs are found


@pytest.mark.asyncio
@pytest.mark.integration
async def test_discover_pdfs_with_llm(test_settings_scraping):
    """Test PDF discovery using LLM extraction when API key is available.

    The API key is loaded from root .env or backend .env via the test_settings_scraping fixture.
    No database or testcontainers needed for this test.
    """
    # Get API key from settings (loaded from config/.env)
    # This will have the value from .env files loaded by the fixture
    openrouter_key = test_settings_scraping.open_router_api_key

    # Runtime check as additional safety (in case skipif didn't catch it)
    if not openrouter_key or openrouter_key == "test_key":
        pytest.skip("open_router_api_key not set or is test key - skipping LLM test")

    # Use a test URL - ideally one with PDFs
    # For a real test, you might want to use a known investor relations page
    test_url = "https://scholar.google.ca/scholar?hl=en&as_sdt=0%2C5&q=ai&btnG="

    async with ScrapingService(openrouter_api_key=openrouter_key) as service:
        # Test with LLM extraction
        pdfs = await service.discover_pdf_urls(test_url, use_llm=True)

        # Assert that we get a result
        assert isinstance(pdfs, list)

        # If PDFs are found, verify they have the expected structure
        if pdfs:
            pdf = pdfs[0]
            assert hasattr(pdf, "url")
            assert hasattr(pdf, "filename")
            assert hasattr(pdf, "fiscal_year")  # May be None
            assert hasattr(pdf, "document_type")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_discover_pdfs_deduplication():
    """Test that PDF URLs are properly deduplicated."""

    test_url = "https://scholar.google.ca/scholar?hl=en&as_sdt=0%2C5&q=ai&btnG="

    async with ScrapingService() as service:
        pdfs = await service.discover_pdf_urls(test_url, use_llm=False)

        # Check for duplicates
        urls = [pdf.url for pdf in pdfs]
        assert len(urls) == len(set(urls)), "Found duplicate URLs in results"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_discover_pdfs_url_resolution():
    """Test that relative URLs are properly resolved to absolute URLs."""
    test_url = "https://scholar.google.ca/scholar?hl=en&as_sdt=0%2C5&q=ai&btnG="

    async with ScrapingService() as service:
        pdfs = await service.discover_pdf_urls(test_url, use_llm=False)

        # All URLs should be absolute (start with http:// or https://)
        for pdf in pdfs:
            assert pdf.url.startswith(("http://", "https://")), f"URL not absolute: {pdf.url}"
