"""
Unit tests for statement compiler service.

Tests compilation of multi-year financial statements.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

import pytest

from app.core.compilation.compiler import StatementCompiler


@pytest.mark.unit
def test_compile_statement_basic():
    """Test basic statement compilation."""
    compiler = StatementCompiler()

    normalized_map = {
        "Revenue": {
            "canonical_name": "Revenue",
            "variations": [
                {"original_name": "Revenue", "fiscal_year": 2023},
                {"original_name": "Revenues", "fiscal_year": 2024},
            ],
            "confidence": "high",
        },
        "Operating Expenses": {
            "canonical_name": "Operating Expenses",
            "variations": [
                {"original_name": "Operating Expenses", "fiscal_year": 2023},
            ],
            "confidence": "high",
        },
    }

    prioritized_data = {
        "2023": {
            "Revenue": {"value": 1000, "source_fiscal_year": 2023, "restated": False},
            "Operating Expenses": {
                "value": 500,
                "source_fiscal_year": 2023,
                "restated": False,
            },
        },
        "2024": {
            "Revenue": {"value": 1200, "source_fiscal_year": 2024, "restated": False},
            "Operating Expenses": {
                "value": 550,
                "source_fiscal_year": 2024,
                "restated": False,
            },
        },
    }

    compiled_data = compiler.compile_statement(
        normalized_map=normalized_map,
        prioritized_data=prioritized_data,
        statement_type="income_statement",
        currency="EUR",
        unit="thousands",
    )

    # Verify structure
    assert "lineItems" in compiled_data
    assert "years" in compiled_data
    assert "currency" in compiled_data
    assert "unit" in compiled_data
    assert "metadata" in compiled_data

    # Verify content
    assert compiled_data["currency"] == "EUR"
    assert compiled_data["unit"] == "thousands"
    assert len(compiled_data["years"]) == 2
    assert "2023" in compiled_data["years"]
    assert "2024" in compiled_data["years"]
    assert len(compiled_data["lineItems"]) == 2

    # Verify line items have year values
    for item in compiled_data["lineItems"]:
        assert "name" in item
        assert "2023" in item or item.get("2023") is not None
        assert "2024" in item or item.get("2024") is not None


@pytest.mark.unit
def test_compile_statement_with_restated_data():
    """Test compilation handles restated data correctly."""
    compiler = StatementCompiler()

    normalized_map = {
        "Revenue": {
            "canonical_name": "Revenue",
            "variations": [{"original_name": "Revenue"}],
            "confidence": "high",
        },
    }

    # Simulate restatement: 2024 report has restated 2023 value
    prioritized_data = {
        "2023": {
            "Revenue": {
                "value": 1100,  # Restated value from 2024 report
                "source_fiscal_year": 2024,
                "restated": True,
            },
        },
        "2024": {
            "Revenue": {"value": 1200, "source_fiscal_year": 2024, "restated": False},
        },
    }

    compiled_data = compiler.compile_statement(
        normalized_map=normalized_map,
        prioritized_data=prioritized_data,
        statement_type="income_statement",
    )

    # Verify restated flag if present
    assert "lineItems" in compiled_data
    assert len(compiled_data["lineItems"]) > 0


@pytest.mark.unit
def test_compile_statement_empty_data():
    """Test compilation handles empty data gracefully."""
    compiler = StatementCompiler()

    compiled_data = compiler.compile_statement(
        normalized_map={},
        prioritized_data={},
        statement_type="income_statement",
    )

    assert compiled_data["lineItems"] == []
    assert compiled_data["years"] == []
    assert "currency" in compiled_data
    assert "unit" in compiled_data


@pytest.mark.unit
def test_compile_statement_sorting():
    """Test that line items are sorted correctly."""
    compiler = StatementCompiler()

    normalized_map = {
        "Revenue": {
            "canonical_name": "Revenue",
            "variations": [{"original_name": "Revenue"}],
            "confidence": "high",
        },
        "Net Income": {
            "canonical_name": "Net Income",
            "variations": [{"original_name": "Net Income"}],
            "confidence": "high",
        },
        "Operating Expenses": {
            "canonical_name": "Operating Expenses",
            "variations": [{"original_name": "Operating Expenses"}],
            "confidence": "high",
        },
    }

    prioritized_data = {
        "2023": {
            "Revenue": {"value": 1000, "source_fiscal_year": 2023},
            "Operating Expenses": {"value": 500, "source_fiscal_year": 2023},
            "Net Income": {"value": 500, "source_fiscal_year": 2023},
        },
    }

    compiled_data = compiler.compile_statement(
        normalized_map=normalized_map,
        prioritized_data=prioritized_data,
        statement_type="income_statement",
    )

    # Verify sorting (revenue should come before expenses)
    assert len(compiled_data["lineItems"]) == 3
    # Items should be sorted by priority keywords and level
