"""
Integration tests for the complete compilation pipeline.

Tests normalization, restatement, and compilation working together
with realistic extraction data (simulated from PDF).

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

from pathlib import Path

import pytest

from app.core.compilation.compiler import StatementCompiler
from app.core.compilation.restatement import RestatementHandler
from app.core.normalization.normalizer import LineItemNormalizer
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
def pdf_extractor() -> PDFExtractor:
    """Create PDF extractor instance."""
    return PDFExtractor()


@pytest.fixture
def mock_extractions():
    """Create mock extraction data simulating what LLM would extract from PDF.

    Simulates extractions from multiple years of AstraZeneca annual reports.
    """
    return [
        # 2023 Annual Report extraction
        {
            "id": 1,
            "document_id": 1,
            "fiscal_year": 2023,
            "raw_data": {
                "line_items": [
                    {
                        "item_name": "Total Revenue",
                        "value": {"2023": 45800.0},
                        "currency": "USD",
                        "unit": "millions",
                    },
                    {
                        "item_name": "Operating Expenses",
                        "value": {"2023": 28000.0},
                        "currency": "USD",
                        "unit": "millions",
                    },
                    {
                        "item_name": "Net Income",
                        "value": {"2023": 8500.0},
                        "currency": "USD",
                        "unit": "millions",
                    },
                ]
            },
        },
        # 2024 Annual Report extraction (contains restated 2023 data)
        {
            "id": 2,
            "document_id": 2,
            "fiscal_year": 2024,
            "raw_data": {
                "line_items": [
                    {
                        "item_name": "Revenue",  # Different name variation
                        "value": {"2023": 45850.0, "2024": 48400.0},  # Restated 2023
                        "currency": "USD",
                        "unit": "millions",
                    },
                    {
                        "item_name": "Operating Expenses",
                        "value": {"2023": 27950.0, "2024": 29000.0},  # Restated 2023
                        "currency": "USD",
                        "unit": "millions",
                    },
                    {
                        "item_name": "Net Income",
                        "value": {"2023": 8600.0, "2024": 9200.0},  # Restated 2023
                        "currency": "USD",
                        "unit": "millions",
                    },
                ]
            },
        },
        # 2022 Annual Report extraction (older, may be overridden)
        {
            "id": 3,
            "document_id": 3,
            "fiscal_year": 2022,
            "raw_data": {
                "line_items": [
                    {
                        "item_name": "Total Revenues",  # Another variation
                        "value": {"2022": 44390.0},
                        "currency": "USD",
                        "unit": "millions",
                    },
                ]
            },
        },
    ]


@pytest.mark.asyncio
@pytest.mark.integration
def test_normalization_with_realistic_data(mock_extractions):
    """Test normalization with realistic extraction data."""
    normalizer = LineItemNormalizer()

    normalized_map = normalizer.normalize_line_items(mock_extractions)

    # Should normalize similar names
    assert len(normalized_map) > 0

    # Check that variations are captured
    for _, entry in normalized_map.items():
        assert "canonical_name" in entry
        assert "variations" in entry
        assert "confidence" in entry
        assert isinstance(entry["variations"], list)
        assert len(entry["variations"]) > 0

    # Verify structure
    # Total Revenue, Revenue, Total Revenues should normalize to same canonical
    has_revenue = False
    for canonical_name, entry in normalized_map.items():
        if "revenue" in canonical_name.lower():
            has_revenue = True
            # Should have multiple variations
            variation_names = [v.get("original_name", "") for v in entry["variations"]]
            # At least one of the variations should be present
            assert any(
                name.lower() in ["total revenue", "revenue", "total revenues"]
                for name in variation_names
            )

    # At least one revenue-related item should be normalized
    assert has_revenue, "Should normalize revenue-related items"


@pytest.mark.asyncio
@pytest.mark.integration
def test_restatement_with_multi_year_data(mock_extractions):
    """Test restatement prioritization with multi-year data."""
    handler = RestatementHandler()

    prioritized_data = handler.prioritize_restated_data(mock_extractions)

    # Verify structure
    assert isinstance(prioritized_data, dict)
    assert len(prioritized_data) > 0

    # 2023 should use restated value from 2024 report
    assert "2023" in prioritized_data
    if "Revenue" in prioritized_data["2023"] or "Total Revenue" in prioritized_data["2023"]:
        # Find the revenue key (could be normalized differently)
        revenue_key = None
        for key in prioritized_data["2023"].keys():
            if "revenue" in key.lower():
                revenue_key = key
                break

        if revenue_key:
            revenue_data = prioritized_data["2023"][revenue_key]
            assert revenue_data["value"] == 45850.0  # Restated value from 2024 report
            assert revenue_data["restated"] is True
            assert revenue_data["source_fiscal_year"] == 2024

    # 2024 should use value from 2024 report
    assert "2024" in prioritized_data
    if "Revenue" in prioritized_data["2024"] or "Total Revenue" in prioritized_data["2024"]:
        revenue_key = None
        for key in prioritized_data["2024"].keys():
            if "revenue" in key.lower():
                revenue_key = key
                break

        if revenue_key:
            revenue_data = prioritized_data["2024"][revenue_key]
            assert revenue_data["value"] == 48400.0  # Current year value
            assert revenue_data["source_fiscal_year"] == 2024


@pytest.mark.asyncio
@pytest.mark.integration
def test_compilation_pipeline_end_to_end(mock_extractions):
    """Test complete pipeline: normalization -> restatement -> compilation."""
    # Step 1: Normalize
    normalizer = LineItemNormalizer()
    normalized_map = normalizer.normalize_line_items(mock_extractions)

    assert len(normalized_map) > 0

    # Step 2: Create name mapping for remapping (as done in compilation worker)
    extraction_with_normalized = []
    for extraction in mock_extractions:
        raw_data = extraction.get("raw_data", {})
        line_items = raw_data.get("line_items", [])
        name_mapping = {}
        for item in line_items:
            original_name = item.get("item_name", "") or item.get("name", "")
            if original_name:
                # Find normalized name
                for canonical, entry in normalized_map.items():
                    variations = entry.get("variations", [])
                    for var in variations:
                        if var.get("original_name") == original_name:
                            name_mapping[original_name] = canonical
                            break

        extraction_copy = extraction.copy()
        extraction_copy["_normalized_names"] = name_mapping
        extraction_with_normalized.append(extraction_copy)

    # Step 3: Restatement (uses original names)
    handler = RestatementHandler()
    prioritized_data = handler.prioritize_restated_data(mock_extractions)

    assert len(prioritized_data) > 0

    # Step 4: Remap prioritized data to normalized names (as done in compilation worker)
    prioritized_normalized = {}
    for year, line_items_year in prioritized_data.items():
        prioritized_normalized[year] = {}
        for original_name, value_data in line_items_year.items():
            # Find normalized name for this original
            normalized_name = original_name  # Default fallback
            for extraction in extraction_with_normalized:
                name_mapping = extraction.get("_normalized_names", {})
                if original_name in name_mapping:
                    normalized_name = name_mapping[original_name]
                    break
            prioritized_normalized[year][normalized_name] = value_data

    # Step 5: Compilation (uses normalized names)
    compiler = StatementCompiler()
    compiled_data = compiler.compile_statement(
        normalized_map=normalized_map,
        prioritized_data=prioritized_normalized,
        statement_type="income_statement",
        currency="USD",
        unit="millions",
    )

    # Verify compilation structure
    assert "lineItems" in compiled_data
    assert "years" in compiled_data
    assert "currency" in compiled_data
    assert "unit" in compiled_data
    assert "metadata" in compiled_data

    # Verify content
    assert compiled_data["currency"] == "USD"
    assert compiled_data["unit"] == "millions"
    assert len(compiled_data["years"]) > 0
    assert len(compiled_data["lineItems"]) > 0

    # Verify line items have year values
    for item in compiled_data["lineItems"]:
        assert "name" in item
        # Should have at least one year value
        has_year_value = False
        for year in compiled_data["years"]:
            if year in item or item.get(year) is not None:
                has_year_value = True
                break
        assert has_year_value, f"Line item {item.get('name')} should have year values"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_pdf_extraction_to_compilation_pipeline(test_pdf_path, pdf_extractor):
    """Test full pipeline from PDF extraction to compilation (with limited pages)."""
    if not pdf_extractor._fitz_available:
        pytest.skip("PyMuPDF (fitz) not available, skipping PDF extraction test")

    # Step 1: Extract from PDF (limited pages for speed)
    pdf_data = await pdf_extractor.extract_from_path(test_pdf_path, max_pages=10)

    # Verify PDF extraction
    assert "text" in pdf_data
    assert len(pdf_data["text"]) > 0

    # Step 2: Create mock extractions based on PDF structure
    # (In real scenario, LLM would extract from pdf_data)
    # For this test, we create realistic mock data
    mock_extractions = [
        {
            "id": 1,
            "document_id": 1,
            "fiscal_year": 2024,
            "raw_data": {
                "line_items": [
                    {
                        "item_name": "Revenue",
                        "value": {"2024": 45000.0},
                        "currency": "USD",
                        "unit": "millions",
                    },
                ]
            },
        }
    ]

    # Step 3: Normalize
    normalizer = LineItemNormalizer()
    normalized_map = normalizer.normalize_line_items(mock_extractions)

    # Step 4: Create name mapping
    extraction_with_normalized = []
    for extraction in mock_extractions:
        raw_data = extraction.get("raw_data", {})
        line_items = raw_data.get("line_items", [])
        name_mapping = {}
        for item in line_items:
            original_name = item.get("item_name", "") or item.get("name", "")
            if original_name:
                for canonical, entry in normalized_map.items():
                    variations = entry.get("variations", [])
                    for var in variations:
                        if var.get("original_name") == original_name:
                            name_mapping[original_name] = canonical
                            break
        extraction_copy = extraction.copy()
        extraction_copy["_normalized_names"] = name_mapping
        extraction_with_normalized.append(extraction_copy)

    # Step 5: Restatement
    handler = RestatementHandler()
    prioritized_data = handler.prioritize_restated_data(mock_extractions)

    # Step 6: Remap to normalized names
    prioritized_normalized = {}
    for year, line_items_year in prioritized_data.items():
        prioritized_normalized[year] = {}
        for original_name, value_data in line_items_year.items():
            normalized_name = original_name
            for extraction in extraction_with_normalized:
                name_mapping = extraction.get("_normalized_names", {})
                if original_name in name_mapping:
                    normalized_name = name_mapping[original_name]
                    break
            prioritized_normalized[year][normalized_name] = value_data

    # Step 7: Compile
    compiler = StatementCompiler()
    compiled_data = compiler.compile_statement(
        normalized_map=normalized_map,
        prioritized_data=prioritized_normalized,
        statement_type="income_statement",
    )

    # Verify end result
    assert "lineItems" in compiled_data
    assert "years" in compiled_data
    assert len(compiled_data["lineItems"]) > 0

    # Verify PDF content was actually extracted (we used real PDF)
    assert pdf_data["page_count"] > 0
    assert len(pdf_data["text"]) > 1000  # Substantial text content
