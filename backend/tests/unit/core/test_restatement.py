"""
Unit tests for restatement handler service.

Tests priority of restated data from newer reports.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

import pytest

from app.core.compilation.restatement import RestatementHandler


@pytest.mark.unit
def test_prioritize_restated_data_basic():
    """Test basic restatement prioritization."""
    handler = RestatementHandler()

    extractions = [
        {
            "id": 1,
            "document_id": 1,
            "fiscal_year": 2023,
            "raw_data": {
                "line_items": [
                    {"item_name": "Revenue", "value": {"2023": 1000}},
                ]
            },
        },
        {
            "id": 2,
            "document_id": 2,
            "fiscal_year": 2024,
            "raw_data": {
                "line_items": [
                    {"item_name": "Revenue", "value": {"2023": 1100, "2024": 1200}},
                ]
            },
        },
    ]

    prioritized_data = handler.prioritize_restated_data(extractions)

    # 2023 should use restated value from 2024 report (1100)
    assert "2023" in prioritized_data
    assert "2024" in prioritized_data
    assert "Revenue" in prioritized_data["2023"]
    assert prioritized_data["2023"]["Revenue"]["value"] == 1100
    assert prioritized_data["2023"]["Revenue"]["restated"] is True
    assert prioritized_data["2023"]["Revenue"]["source_fiscal_year"] == 2024


@pytest.mark.unit
def test_prioritize_restated_data_newer_overrides_older():
    """Test that newer reports override older values."""
    handler = RestatementHandler()

    extractions = [
        {
            "id": 1,
            "document_id": 1,
            "fiscal_year": 2022,
            "raw_data": {
                "line_items": [
                    {"item_name": "Revenue", "value": {"2022": 900}},
                ]
            },
        },
        {
            "id": 2,
            "document_id": 2,
            "fiscal_year": 2023,
            "raw_data": {
                "line_items": [
                    {"item_name": "Revenue", "value": {"2022": 950, "2023": 1000}},
                ]
            },
        },
        {
            "id": 3,
            "document_id": 3,
            "fiscal_year": 2024,
            "raw_data": {
                "line_items": [
                    {"item_name": "Revenue", "value": {"2022": 1000, "2023": 1100, "2024": 1200}},
                ]
            },
        },
    ]

    prioritized_data = handler.prioritize_restated_data(extractions)

    # 2022 should use restated value from 2024 report (1000)
    assert prioritized_data["2022"]["Revenue"]["value"] == 1000
    assert prioritized_data["2022"]["Revenue"]["source_fiscal_year"] == 2024

    # 2023 should use restated value from 2024 report (1100)
    assert prioritized_data["2023"]["Revenue"]["value"] == 1100
    assert prioritized_data["2023"]["Revenue"]["source_fiscal_year"] == 2024

    # 2024 should use value from 2024 report (1200)
    assert prioritized_data["2024"]["Revenue"]["value"] == 1200
    assert prioritized_data["2024"]["Revenue"]["source_fiscal_year"] == 2024


@pytest.mark.unit
def test_prioritize_restated_data_empty_extractions():
    """Test handler handles empty extractions gracefully."""
    handler = RestatementHandler()

    prioritized_data = handler.prioritize_restated_data([])

    assert isinstance(prioritized_data, dict)
    assert len(prioritized_data) == 0


@pytest.mark.unit
def test_prioritize_restated_data_missing_fields():
    """Test handler handles extractions with missing fields."""
    handler = RestatementHandler()

    extractions = [
        {
            "id": 1,
            "raw_data": {
                "line_items": [
                    {"item_name": "Revenue", "value": {"2023": 1000}},
                ]
            },
        },
    ]

    prioritized_data = handler.prioritize_restated_data(extractions)

    # Should handle gracefully
    assert isinstance(prioritized_data, dict)
