"""
PDF preprocessor for extracting relevant sections and reducing token usage.

Identifies financial statement sections and extracts only relevant pages
to minimize LLM API costs.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)


class PDFPreprocessor:
    """Preprocess PDF content to extract relevant sections for LLM extraction."""

    # Keywords to locate financial statement sections
    SECTION_KEYWORDS = {
        "income_statement": [
            "income statement",
            "statement of operations",
            "profit and loss",
            "profit & loss",
            "p&l",
            "consolidated income",
            "statement of comprehensive income",
            "results of operations",
        ],
        "balance_sheet": [
            "balance sheet",
            "statement of financial position",
            "consolidated balance",
            "assets and liabilities",
            "statement of financial condition",
        ],
        "cash_flow_statement": [
            "cash flow statement",
            "statement of cash flows",
            "consolidated cash",
            "cash flows from operating activities",
            "cash flows from investing activities",
            "cash flows from financing activities",
        ],
    }

    def preprocess_for_statement(
        self,
        extracted_content: dict[str, Any],
        statement_type: str,
        max_chars: int = 50000,
    ) -> str:
        """Extract relevant section for a specific statement type.

        Args:
            extracted_content: Dictionary with 'text' and 'tables' from PDFExtractor.
            statement_type: Type of statement (income_statement, balance_sheet, cash_flow_statement).
            max_chars: Maximum characters to return (default: 50000).

        Returns:
            Preprocessed text content focused on the statement type.
        """
        full_text = extracted_content.get("text", "")
        keywords = self.SECTION_KEYWORDS.get(statement_type, [])

        if not keywords:
            logger.warning(f"Unknown statement type: {statement_type}, returning first {max_chars} chars")
            return self._truncate_text(full_text, max_chars)

        # Find section start
        lines = full_text.split("\n")
        section_start = self._find_section_start(lines, keywords)

        if section_start is None:
            logger.warning(
                f"Could not locate {statement_type} section using keywords: {keywords}. "
                "Returning first part of document."
            )
            return self._truncate_text(full_text, max_chars)

        # Extract section with buffer (5 lines before, 200 lines after)
        section_end = min(section_start + 200, len(lines))
        section_start_safe = max(0, section_start - 5)
        relevant_lines = lines[section_start_safe:section_end]
        relevant_text = "\n".join(relevant_lines)

        # Remove page artifacts
        cleaned_text = self._remove_page_artifacts(relevant_text)

        # Include financial table data extracted by camelot if available
        financial_tables = extracted_content.get("financial_tables", [])
        table_text = self._format_financial_tables(financial_tables, statement_type)
        if table_text:
            cleaned_text = (
                f"EXTRACTED TABLE DATA:\n{table_text}\n\n"
                f"DOCUMENT TEXT:\n{cleaned_text}"
            )

        # Truncate if needed
        if len(cleaned_text) > max_chars:
            logger.info(
                f"Truncating {statement_type} section from {len(cleaned_text)} "
                f"to {max_chars} characters"
            )
            cleaned_text = self._truncate_text(cleaned_text, max_chars)

        logger.info(
            f"Preprocessed {statement_type}: {len(cleaned_text)} chars "
            f"(from line {section_start_safe} to {section_end}), "
            f"{len(financial_tables)} financial tables included"
        )

        return cleaned_text

    def _find_section_start(self, lines: list[str], keywords: list[str]) -> int | None:
        """Find the line number where a financial statement section starts.

        Skips Table of Contents entries (lines with trailing dots/page numbers)
        and prefers matches in the second half of the document where financial
        statements typically appear in annual reports.

        Args:
            lines: List of text lines.
            keywords: Keywords to search for.

        Returns:
            Line number where section starts, or None if not found.
        """
        candidates = []

        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            if not any(keyword in line_lower for keyword in keywords):
                continue

            # Skip TOC-like lines: trailing dots + page number, or trailing page number
            if re.search(r"\.{2,}\s*\d+\s*$", line_lower):
                continue
            if re.search(r"\s{3,}\d{1,3}\s*$", line_lower):
                continue

            candidates.append(i)

        if not candidates:
            return None

        # Prefer matches in the second half of the document (where statements are)
        midpoint = len(lines) // 2
        second_half = [c for c in candidates if c >= midpoint]
        if second_half:
            return second_half[0]

        # Fall back to last match in first half (closer to the actual content)
        return candidates[-1]

    def _remove_page_artifacts(self, text: str) -> str:
        """Remove page numbers, headers, and footers from text.

        Args:
            text: Raw text content.

        Returns:
            Cleaned text.
        """
        lines = text.split("\n")
        cleaned_lines = []

        for line in lines:
            # Skip lines that are likely page numbers or headers
            line_stripped = line.strip()

            # Skip pure numbers (likely page numbers)
            if line_stripped.isdigit() and len(line_stripped) < 4:
                continue

            # Skip common header/footer patterns
            if any(
                pattern in line_lower
                for pattern in ["page ", "confidential", "proprietary"]
                for line_lower in [line_stripped.lower()]
            ):
                continue

            cleaned_lines.append(line)

        return "\n".join(cleaned_lines)

    def _format_financial_tables(
        self, financial_tables: list[dict[str, Any]], statement_type: str
    ) -> str:
        """Format extracted financial tables as text for LLM context.

        Args:
            financial_tables: List of table dicts from PDFExtractor.
            statement_type: Target statement type to filter relevant tables.

        Returns:
            Formatted string of table data, or empty string if none relevant.
        """
        if not financial_tables:
            return ""

        # Keywords to identify tables relevant to this statement type
        relevance_keywords = self.SECTION_KEYWORDS.get(statement_type, [])

        formatted_parts = []
        for table in financial_tables:
            df_data = table.get("df", [])
            if not df_data or not isinstance(df_data, list):
                continue

            # Flatten table text to check relevance
            table_text_flat = ""
            for row in df_data:
                if isinstance(row, dict):
                    table_text_flat += " ".join(str(v) for v in row.values()).lower()

            # Check if this table is relevant to the target statement type
            if relevance_keywords and not any(
                kw in table_text_flat for kw in relevance_keywords
            ):
                continue

            # Format table as text rows
            rows = []
            for row in df_data:
                if isinstance(row, dict):
                    cells = [str(v) for v in row.values() if v]
                    if cells:
                        rows.append(" | ".join(cells))

            if rows:
                page_info = f" (page {table.get('page', '?')})"
                formatted_parts.append(
                    f"--- Table{page_info} ---\n" + "\n".join(rows)
                )

        return "\n\n".join(formatted_parts)

    def _truncate_text(self, text: str, max_chars: int) -> str:
        """Truncate text to maximum character count.

        Args:
            text: Text to truncate.
            max_chars: Maximum characters.

        Returns:
            Truncated text.
        """
        if len(text) <= max_chars:
            return text

        # Try to truncate at a sentence boundary
        truncated = text[:max_chars]
        last_period = truncated.rfind(".")
        last_newline = truncated.rfind("\n")

        # Use whichever is closer to the end
        if last_period > max_chars - 500:  # Within 500 chars of limit
            return text[: last_period + 1]
        elif last_newline > max_chars - 200:  # Within 200 chars of limit
            return text[: last_newline + 1]

        return truncated + "..."
