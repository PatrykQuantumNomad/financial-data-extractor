"""
Unit tests for log filter utilities.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

import logging

import pytest

from app.utils.log_filter import SuppressSpecificLogEntries


@pytest.mark.unit
class TestLogFilter:
    """Test cases for log filter utilities."""

    def test_suppress_specific_log_entries_allows_normal_log(self):
        """Test filter allows normal log messages."""
        # Arrange
        filter_obj = SuppressSpecificLogEntries(["suppressed_message"])
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="This is a normal log message",
            args=(),
            exc_info=None,
        )

        # Act
        result = filter_obj.filter(record)

        # Assert
        assert result is True

    def test_suppress_specific_log_entries_blocks_suppressed_log(self):
        """Test filter blocks log messages containing suppressed strings."""
        # Arrange
        filter_obj = SuppressSpecificLogEntries(["suppressed_message"])
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="This contains suppressed_message and should be filtered",
            args=(),
            exc_info=None,
        )

        # Act
        result = filter_obj.filter(record)

        # Assert
        assert result is False

    def test_suppress_specific_log_entries_multiple_suppressed_strings(self):
        """Test filter with multiple suppressed strings."""
        # Arrange
        filter_obj = SuppressSpecificLogEntries(["error1", "error2"])

        # Test first suppressed string
        record1 = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="This contains error1",
            args=(),
            exc_info=None,
        )

        # Test second suppressed string
        record2 = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="This contains error2",
            args=(),
            exc_info=None,
        )

        # Act
        result1 = filter_obj.filter(record1)
        result2 = filter_obj.filter(record2)

        # Assert
        assert result1 is False
        assert result2 is False

    def test_suppress_specific_log_entries_case_sensitive(self):
        """Test filter is case sensitive."""
        # Arrange
        filter_obj = SuppressSpecificLogEntries(["Error"])

        # Lowercase version should not be blocked
        record1 = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="This contains error (lowercase)",
            args=(),
            exc_info=None,
        )

        # Uppercase version should be blocked
        record2 = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="This contains Error (uppercase)",
            args=(),
            exc_info=None,
        )

        # Act
        result1 = filter_obj.filter(record1)
        result2 = filter_obj.filter(record2)

        # Assert
        assert result1 is True
        assert result2 is False
