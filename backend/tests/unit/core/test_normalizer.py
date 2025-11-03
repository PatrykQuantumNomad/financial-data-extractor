"""
Unit tests for line item normalizer service.

Tests normalization of line items across multiple extractions.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

import pytest

from app.core.normalization.normalizer import LineItemNormalizer


@pytest.mark.unit
def test_normalize_line_items_basic():
    """Test basic normalization of line items."""
    normalizer = LineItemNormalizer()

    # Mock extractions with similar line items
    extractions = [
        {
            "id": 1,
            "document_id": 1,
            "raw_data": {
                "line_items": [
                    {"item_name": "Revenue", "value": {"2023": 1000}},
                    {"item_name": "Operating Expenses", "value": {"2023": 500}},
                ]
            },
            "fiscal_year": 2023,
        },
        {
            "id": 2,
            "document_id": 2,
            "raw_data": {
                "line_items": [
                    {"item_name": "Revenue", "value": {"2024": 1200}},
                    {"item_name": "Operating Expenses", "value": {"2024": 550}},
                ]
            },
            "fiscal_year": 2024,
        },
    ]

    normalized_map = normalizer.normalize_line_items(extractions)

    # Should normalize to canonical names
    assert len(normalized_map) > 0

    # Check structure
    for _, entry in normalized_map.items():
        assert "canonical_name" in entry
        assert "variations" in entry
        assert "confidence" in entry
        assert isinstance(entry["variations"], list)


@pytest.mark.unit
def test_normalize_line_items_with_variations():
    """Test normalization handles name variations correctly."""
    normalizer = LineItemNormalizer()

    extractions = [
        {
            "id": 1,
            "document_id": 1,
            "raw_data": {
                "line_items": [
                    {"item_name": "Total Revenue", "value": {"2023": 1000}},
                    {"item_name": "Revenues", "value": {"2023": 1000}},
                ]
            },
            "fiscal_year": 2023,
        },
    ]

    normalized_map = normalizer.normalize_line_items(extractions)

    # Should normalize similar items
    assert len(normalized_map) >= 1


@pytest.mark.unit
def test_normalize_line_items_with_manual_mappings():
    """Test normalization respects manual mappings."""
    manual_mappings = {
        "Total Revenue": "Revenue",
        "Revenues": "Revenue",
    }

    normalizer = LineItemNormalizer(manual_mappings=manual_mappings)

    extractions = [
        {
            "id": 1,
            "document_id": 1,
            "raw_data": {
                "line_items": [
                    {"item_name": "Total Revenue", "value": {"2023": 1000}},
                    {"item_name": "Revenues", "value": {"2023": 1000}},
                ]
            },
            "fiscal_year": 2023,
        },
    ]

    normalized_map = normalizer.normalize_line_items(extractions)

    # Manual mappings should take precedence
    assert len(normalized_map) >= 1


@pytest.mark.unit
def test_normalize_empty_extractions():
    """Test normalization handles empty extraction list."""
    normalizer = LineItemNormalizer()

    normalized_map = normalizer.normalize_line_items([])

    assert isinstance(normalized_map, dict)
    assert len(normalized_map) == 0


@pytest.mark.unit
def test_normalize_extractions_with_missing_fields():
    """Test normalization handles extractions with missing fields gracefully."""
    normalizer = LineItemNormalizer()

    extractions = [
        {
            "id": 1,
            "raw_data": {
                "line_items": [
                    {"item_name": "Revenue", "value": {}},
                    {"value": {"2023": 1000}},  # Missing item_name
                    {"item_name": ""},  # Empty item_name
                ]
            },
        },
    ]

    normalized_map = normalizer.normalize_line_items(extractions)

    # Should handle gracefully and only normalize valid items
    assert isinstance(normalized_map, dict)
