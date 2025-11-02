"""
Unit tests for file utilities.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

import json
import tempfile
from pathlib import Path

import pytest

from app.core.exceptions.api_exceptions import (
    JSONFileNotFoundError,
    JSONInvalidEncodingError,
    JSONInvalidError,
)
from app.utils.file_utils import load_json_file


@pytest.mark.unit
class TestFileUtils:
    """Test cases for file utility functions."""

    def test_load_json_file_success(self):
        """Test successful JSON file loading."""
        # Arrange
        test_data = {"name": "Test Company", "ticker": "TEST"}
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump(test_data, f)
            temp_file = f.name

        try:
            # Act
            result = load_json_file(temp_file)

            # Assert
            assert result == test_data
            assert result["name"] == "Test Company"
        finally:
            # Cleanup
            Path(temp_file).unlink()

    def test_load_json_file_with_complex_data(self):
        """Test loading JSON file with complex nested data."""
        # Arrange
        test_data = {
            "company": {
                "name": "Test Company",
                "financials": {"revenue": 1000000, "expenses": 800000},
            }
        }
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump(test_data, f)
            temp_file = f.name

        try:
            # Act
            result = load_json_file(temp_file)

            # Assert
            assert result["company"]["name"] == "Test Company"
            assert result["company"]["financials"]["revenue"] == 1000000
        finally:
            # Cleanup
            Path(temp_file).unlink()

    def test_load_json_file_not_found(self):
        """Test loading non-existent JSON file raises FileNotFoundError."""
        # Arrange
        non_existent_file = "/path/to/non/existent/file.json"

        # Act & Assert
        with pytest.raises(JSONFileNotFoundError):
            load_json_file(non_existent_file)

    def test_load_json_file_invalid_json(self):
        """Test loading invalid JSON file raises JSONInvalidError."""
        # Arrange
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            f.write("{ invalid json }")
            temp_file = f.name

        try:
            # Act & Assert
            with pytest.raises(JSONInvalidError):
                load_json_file(temp_file)
        finally:
            # Cleanup
            Path(temp_file).unlink()

    def test_load_json_file_invalid_encoding(self):
        """Test loading file with invalid encoding raises JSONInvalidEncodingError."""
        # Arrange
        # Create a file with invalid UTF-8 encoding
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".json", delete=False) as f:
            # Write invalid UTF-8 sequence
            f.write(b"\xff\xfe")  # BOM + invalid sequence
            temp_file = f.name

        try:
            # Act & Assert
            with pytest.raises(JSONInvalidEncodingError):
                load_json_file(temp_file)
        finally:
            # Cleanup
            Path(temp_file).unlink()

    def test_load_json_file_empty_json(self):
        """Test loading empty JSON file."""
        # Arrange
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            f.write("{}")
            temp_file = f.name

        try:
            # Act
            result = load_json_file(temp_file)

            # Assert
            assert result == {}
        finally:
            # Cleanup
            Path(temp_file).unlink()

    def test_load_json_file_with_list(self):
        """Test loading JSON file containing a list."""
        # Arrange
        test_data = [{"id": 1, "name": "Company 1"}, {"id": 2, "name": "Company 2"}]
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump(test_data, f)
            temp_file = f.name

        try:
            # Act
            result = load_json_file(temp_file)

            # Assert
            assert isinstance(result, list)
            assert len(result) == 2
            assert result[0]["name"] == "Company 1"
        finally:
            # Cleanup
            Path(temp_file).unlink()
