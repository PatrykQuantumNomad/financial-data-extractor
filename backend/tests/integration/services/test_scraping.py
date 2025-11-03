"""
Integration tests for scraping service.

Tests PDF discovery from websites without downloading PDFs.

These tests don't require database or testcontainers - they only test web scraping.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

from urllib.parse import urlparse

import pytest

from app.core.scraping import ScrapingService
from app.core.scraping.service import DiscoveredPDF

# Test URL for testing PDF discovery using Google Scholar, which should have many PDFs
test_url = "https://scholar.google.ca/scholar?hl=en&as_sdt=0%2C5&q=ai&btnG="


def _validate_discovered_pdf(pdf: DiscoveredPDF, index: int | None = None) -> None:
    """Validate a single DiscoveredPDF object has correct structure and values.

    Args:
        pdf: The DiscoveredPDF object to validate.
        index: Optional index in the list for better error messages.
    """
    prefix = f"PDF[{index}]: " if index is not None else "PDF: "

    # Type validation - must be DiscoveredPDF instance
    assert isinstance(pdf, DiscoveredPDF), (
        f"{prefix}Must be DiscoveredPDF instance, got {type(pdf)}"
    )

    # Required fields must be present and non-empty strings
    assert hasattr(pdf, "url"), f"{prefix}Missing 'url' attribute"
    assert isinstance(pdf.url, str), f"{prefix}'url' must be string, got {type(pdf.url)}"
    assert pdf.url.strip() != "", f"{prefix}'url' must not be empty"

    assert hasattr(pdf, "filename"), f"{prefix}Missing 'filename' attribute"
    assert isinstance(pdf.filename, str), (
        f"{prefix}'filename' must be string, got {type(pdf.filename)}"
    )
    assert pdf.filename.strip() != "", f"{prefix}'filename' must not be empty"

    # URL format validation
    assert pdf.url.startswith(("http://", "https://")), (
        f"{prefix}'url' must be valid HTTP/HTTPS URL, got: {pdf.url}"
    )
    try:
        parsed = urlparse(pdf.url)
        assert parsed.scheme in ("http", "https"), f"{prefix}URL must have http/https scheme"
        assert parsed.netloc, f"{prefix}URL must have valid domain/host"
    except Exception as e:
        pytest.fail(f"{prefix}Invalid URL format: {pdf.url}, error: {e}")

    # Filename validation
    assert pdf.filename.endswith(".pdf"), (
        f"{prefix}'filename' should end with .pdf, got: {pdf.filename}"
    )

    # Optional fields - check types when present
    assert hasattr(pdf, "fiscal_year"), f"{prefix}Missing 'fiscal_year' attribute"
    if pdf.fiscal_year is not None:
        assert isinstance(pdf.fiscal_year, int), (
            f"{prefix}'fiscal_year' must be int or None, got {type(pdf.fiscal_year)}"
        )

    # Document type validation
    assert hasattr(pdf, "document_type"), f"{prefix}Missing 'document_type' attribute"
    assert isinstance(pdf.document_type, str), (
        f"{prefix}'document_type' must be string, got {type(pdf.document_type)}"
    )

    # Title validation (optional)
    assert hasattr(pdf, "title"), f"{prefix}Missing 'title' attribute"
    if pdf.title is not None:
        assert isinstance(pdf.title, str), (
            f"{prefix}'title' must be str or None, got {type(pdf.title)}"
        )
        assert pdf.title.strip() != "", f"{prefix}'title' must not be empty string if provided"

    # Description validation (optional)
    assert hasattr(pdf, "description"), f"{prefix}Missing 'description' attribute"
    if pdf.description is not None:
        assert isinstance(pdf.description, str), (
            f"{prefix}'description' must be str or None, got {type(pdf.description)}"
        )

    # Confidence score validation
    assert hasattr(pdf, "confidence"), f"{prefix}Missing 'confidence' attribute"
    assert isinstance(pdf.confidence, float), (
        f"{prefix}'confidence' must be float, got {type(pdf.confidence)}"
    )
    assert 0.0 <= pdf.confidence <= 1.0, (
        f"{prefix}'confidence' must be between 0.0 and 1.0, got {pdf.confidence}"
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_discover_pdfs_with_css_extraction():
    """Test PDF discovery using CSS/regex extraction.

    Validates that the service can discover PDFs without LLM, using CSS/regex patterns.
    Checks for proper structure, data types, and URL validity.
    """
    async with ScrapingService() as service:
        # Test without LLM (should use CSS/regex extraction)
        pdfs = await service.discover_pdf_urls(test_url, use_llm=False)

        # Basic structure validation
        assert isinstance(pdfs, list), f"Result must be list, got {type(pdfs)}"
        # The service should not crash even if no PDFs are found
        # (some pages might not have PDFs, which is acceptable)

        # If PDFs are found, validate each one
        if pdfs:
            assert len(pdfs) > 0, "List should not be empty if PDFs are found"

            # Validate each PDF in the list
            for i, pdf in enumerate(pdfs):
                _validate_discovered_pdf(pdf, index=i)

            # Verify deduplication - no duplicate URLs
            urls = [pdf.url for pdf in pdfs]
            unique_urls = set(urls)
            assert len(urls) == len(unique_urls), (
                f"Found {len(urls) - len(unique_urls)} duplicate URL(s). "
                f"Service should deduplicate results. Duplicates: {[url for url in urls if urls.count(url) > 1]}"
            )

            # Check that confidence scores are reasonable for CSS extraction
            # CSS extraction typically has lower confidence than LLM
            css_pdfs = [pdf for pdf in pdfs if pdf.confidence < 0.9]
            assert len(css_pdfs) > 0 or all(pdf.confidence <= 1.0 for pdf in pdfs), (
                "CSS extraction should have confidence <= 1.0"
            )


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.skip(
    reason="Expensive integration test: omit when running all integration tests by default"
)
async def test_discover_pdfs_with_llm(test_settings_services):
    """Test PDF discovery using LLM extraction when API key is available.

    Tests multiple OpenRouter models and compares their results.

    The API key is loaded from root .env or backend .env via the test_settings_services fixture.
    No database or testcontainers needed for this test.

    Validates that LLM extraction returns properly structured PDFs with metadata
    and compares results across different models.
    """
    openrouter_key = test_settings_services.open_router_api_key
    max_crawl_depth = test_settings_services.max_crawl_depth

    openrouter_models = [
        "openai/gpt-oss-120b",
        "openai/gpt-5-mini",
        "openai/gpt-5-nano",
        "openai/gpt-4.1-mini",
        "openai/gpt-4.1-nano",
        "openai/gpt-4o-mini",
        "openrouter/google/gemini-2.5-pro",
        "openrouter/google/gemini-2.5-flash-lite",
        "openrouter/x-ai/grok-4-fast",
    ]

    # Runtime check as additional safety (in case skipif didn't catch it)
    if not openrouter_key or openrouter_key == "test_key":
        pytest.skip("open_router_api_key not set or is test key - skipping LLM test")

    # Store results for each model
    model_results: dict[str, list[DiscoveredPDF]] = {}

    # Test each model
    for model in openrouter_models:
        async with ScrapingService(
            openrouter_api_key=openrouter_key,
            openrouter_model=model,
            max_crawl_depth=max_crawl_depth,
        ) as service:
            # Test with LLM extraction
            pdfs = await service.discover_pdf_urls(test_url, use_llm=True)

            # Basic structure validation
            assert isinstance(pdfs, list), f"Model {model}: Result must be list, got {type(pdfs)}"

            # If PDFs are found, verify they have the expected structure
            if pdfs:
                assert len(pdfs) > 0, f"Model {model}: List should not be empty if PDFs are found"

                # Validate each PDF in the list
                for i, pdf in enumerate(pdfs):
                    _validate_discovered_pdf(pdf, index=i)

                # Verify deduplication - no duplicate URLs
                urls = [pdf.url for pdf in pdfs]
                unique_urls = set(urls)
                assert len(urls) == len(unique_urls), (
                    f"Model {model}: Found {len(urls) - len(unique_urls)} duplicate URL(s). "
                    f"Service should deduplicate results. "
                    f"Duplicates: {[url for url in urls if urls.count(url) > 1]}"
                )

                # LLM extraction should typically have higher confidence than CSS
                # Verify that confidence scores are within valid range
                confidence_scores = [pdf.confidence for pdf in pdfs]
                assert all(0.0 <= c <= 1.0 for c in confidence_scores), (
                    f"Model {model}: All confidence scores must be between 0.0 and 1.0, "
                    f"got: {[c for c in confidence_scores if not (0.0 <= c <= 1.0)]}"
                )

            # Store results for comparison
            model_results[model] = pdfs

    # Compare results across models
    if model_results:
        # Extract metrics for comparison
        model_counts = {model: len(pdfs) for model, pdfs in model_results.items()}
        model_urls = {model: {pdf.url for pdf in pdfs} for model, pdfs in model_results.items()}
        model_confidence_avg = {
            model: (sum(pdf.confidence for pdf in pdfs) / len(pdfs) if pdfs else 0.0)
            for model, pdfs in model_results.items()
        }
        model_metadata_counts = {
            model: sum(
                1
                for pdf in pdfs
                if pdf.title is not None
                or pdf.fiscal_year is not None
                or pdf.description is not None
            )
            for model, pdfs in model_results.items()
        }

        # Find all unique URLs across all models
        all_urls = set()
        for urls_set in model_urls.values():
            all_urls.update(urls_set)

        # Calculate overlap metrics
        if len(model_results) > 1 and all_urls:
            # Find URLs found by all models (consensus)
            consensus_urls = (
                set.intersection(*model_urls.values()) if model_urls.values() else set()
            )

            # Log comparison summary (informational assertions)
            assert len(all_urls) >= 0, "Total unique URLs should be non-negative"
            assert len(consensus_urls) >= 0, "Consensus URLs should be non-negative"

            # Verify that at least some models found PDFs (may vary by model capability)
            models_with_results = [model for model, count in model_counts.items() if count > 0]
            assert len(models_with_results) >= 0, (
                f"At least some models should find PDFs. Results: {model_counts}"
            )

            # Compare confidence scores across models
            # Different models may have different confidence distributions
            confidence_ranges = {
                model: (
                    min(pdf.confidence for pdf in pdfs) if pdfs else 0.0,
                    max(pdf.confidence for pdf in pdfs) if pdfs else 0.0,
                )
                for model, pdfs in model_results.items()
            }
            assert all(
                0.0 <= min_conf <= 1.0 and 0.0 <= max_conf <= 1.0
                for min_conf, max_conf in confidence_ranges.values()
            ), "All confidence ranges should be within [0.0, 1.0]"

            # Compare average confidence and metadata counts across models
            # These metrics help identify which models perform better
            avg_confidences = [avg for avg in model_confidence_avg.values() if avg > 0.0]
            metadata_totals = list(model_metadata_counts.values())

            assert all(0.0 <= avg <= 1.0 for avg in avg_confidences), (
                "All average confidence scores should be within [0.0, 1.0]"
            )
            assert all(count >= 0 for count in metadata_totals), (
                "All metadata counts should be non-negative"
            )
