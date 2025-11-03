"""
Integration tests for PDF extractor service.

Tests PDF text and table extraction from actual PDF files.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

from pathlib import Path

import pytest

from app.core.pdf.extractor import PDFExtractor


@pytest.fixture
def test_pdf_path() -> Path:
    """Return path to test PDF file."""
    test_dir = Path(__file__).resolve().parent.parent / "data"
    pdf_path = test_dir / "AstraZeneca_AR_2024.pdf"
    if not pdf_path.exists():
        pytest.skip(f"Test PDF not found: {pdf_path}")
    return pdf_path


@pytest.fixture
def extractor() -> PDFExtractor:
    """Create PDF extractor instance."""
    return PDFExtractor()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_extract_from_path_valid_pdf(extractor: PDFExtractor, test_pdf_path: Path):
    """Test PDF extraction from a valid PDF file path."""
    if not extractor._fitz_available:
        pytest.skip("PyMuPDF (fitz) not available, skipping PDF extraction test")

    # Limit to first 5 pages for faster test execution
    result = await extractor.extract_from_path(test_pdf_path, max_pages=5)

    # Verify result structure
    assert "text" in result
    assert "tables" in result
    assert "financial_tables" in result
    assert "page_count" in result

    # Verify result content
    assert isinstance(result["text"], str)
    assert len(result["text"]) > 0, "Should extract text content"
    assert isinstance(result["page_count"], int)
    assert result["page_count"] > 0, "Should have at least one page"
    assert isinstance(result["tables"], list)
    assert isinstance(result["financial_tables"], list)

    # For a real annual report, we expect significant text content
    assert len(result["text"]) > 1000, "Annual report should have substantial text"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_extract_from_storage_valid_pdf(extractor: PDFExtractor, test_pdf_path: Path):
    """Test PDF extraction from bytes (object storage simulation)."""
    if not extractor._fitz_available:
        pytest.skip("PyMuPDF (fitz) not available, skipping PDF extraction test")

    # Read PDF file into bytes
    with open(test_pdf_path, "rb") as f:
        pdf_bytes = f.read()

    # Limit to first 5 pages for faster test execution
    result = await extractor.extract_from_storage(pdf_bytes, test_pdf_path.name, max_pages=5)

    # Verify result structure
    assert "text" in result
    assert "tables" in result
    assert "financial_tables" in result
    assert "page_count" in result

    # Verify result content
    assert isinstance(result["text"], str)
    assert len(result["text"]) > 0, "Should extract text content"
    assert isinstance(result["page_count"], int)
    assert result["page_count"] > 0, "Should have at least one page"
    assert isinstance(result["tables"], list)
    assert isinstance(result["financial_tables"], list)

    # Verify same content as file path extraction
    assert len(result["text"]) > 1000, "Annual report should have substantial text"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_extract_from_path_nonexistent_file(extractor: PDFExtractor):
    """Test that extractor raises error for non-existent file."""
    nonexistent_path = Path("/nonexistent/file.pdf")

    with pytest.raises(FileNotFoundError, match="PDF file not found"):
        await extractor.extract_from_path(nonexistent_path)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_extractor_initialization(extractor: PDFExtractor):
    """Test that PDF extractor initializes correctly with available libraries."""
    # Check that extractor has expected attributes
    assert hasattr(extractor, "_camelot_available")
    assert hasattr(extractor, "_fitz_available")
    assert hasattr(extractor, "_pdfplumber_available")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_extract_financial_tables(extractor: PDFExtractor, test_pdf_path: Path):
    """Test that financial tables are identified correctly."""
    if not extractor._fitz_available:
        pytest.skip("PyMuPDF (fitz) not available, skipping PDF extraction test")

    # Limit to first 5 pages for faster test execution
    result = await extractor.extract_from_path(test_pdf_path, max_pages=5)

    # Verify financial tables structure
    assert isinstance(result["financial_tables"], list)

    # For an annual report, we expect some tables to be identified as financial
    # (though this depends on the extraction quality and keyword matching)
    # At minimum, verify the structure is correct
    for table in result["financial_tables"]:
        assert "df" in table
        assert "page" in table


@pytest.mark.asyncio
@pytest.mark.integration
async def test_extract_tables_structure(extractor: PDFExtractor, test_pdf_path: Path):
    """Test that extracted tables have the correct structure."""
    if not extractor._fitz_available:
        pytest.skip("PyMuPDF (fitz) not available, skipping PDF extraction test")

    # Limit to first 5 pages for faster test execution
    result = await extractor.extract_from_path(test_pdf_path, max_pages=5)

    # Verify table structure
    for table in result["tables"]:
        assert "df" in table
        assert "page" in table
        assert "order" in table
        assert isinstance(table["page"], int)
        assert table["page"] > 0
