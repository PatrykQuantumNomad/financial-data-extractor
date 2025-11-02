"""
This module provides a logging filter to suppress specific
log records based on their content.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

import logging


class SuppressSpecificLogEntries(logging.Filter):
    """
    A logging filter to suppress log records containing specific strings.

    Attributes:
        suppressed_entries (list): A list of strings to be suppressed in logs.

    Methods:
        filter(record: logging.LogRecord) -> bool:
            Determines if the log record should be suppressed based on its message content.
    """

    def __init__(self, suppressed_entries: list[str]):
        """
        Initializes the SuppressSpecificLogEntries filter with a list of strings to suppress.

        Args:
            suppressed_entries (List[str]): A list of strings to be suppressed in logs.
        """
        super().__init__()
        self.suppressed_entries = suppressed_entries

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Checks if the log record's message contains any of the suppressed strings.

        Args:
            record (logging.LogRecord): The log record to be checked.

        Returns:
            bool: True if the log record should be allowed, False if it should be suppressed.
        """
        return not any(entry in record.getMessage() for entry in self.suppressed_entries)
