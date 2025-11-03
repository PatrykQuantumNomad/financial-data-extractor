"""
Financial term synonyms for exact matching.

Provides common synonyms and variations for financial line items.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""


class FinancialSynonyms:
    """Financial term synonyms dictionary."""

    # Common synonyms for major line items
    SYNONYMS: dict[str, list[str]] = {
        # Revenue variations
        "revenue": [
            "revenues",
            "total revenue",
            "sales",
            "net sales",
            "turnover",
            "net turnover",
            "net revenue",
            "revenue, net",
        ],
        # Cost of revenue variations
        "cost of revenue": [
            "cost of revenues",
            "cost of sales",
            "cost of goods sold",
            "cogs",
            "cost of products sold",
        ],
        # Gross profit variations
        "gross profit": [
            "gross income",
            "gross margin",
            "gross earnings",
        ],
        # Operating expenses
        "operating expenses": [
            "operating costs",
            "opex",
            "operating expenditure",
        ],
        # Operating income
        "operating income": [
            "operating profit",
            "operating earnings",
            "ebit",
            "earnings before interest and taxes",
        ],
        # Net income
        "net income": [
            "net profit",
            "net earnings",
            "profit for the period",
            "net result",
        ],
        # Assets
        "total assets": [
            "assets, total",
            "total assets, end of period",
        ],
        # Liabilities
        "total liabilities": [
            "liabilities, total",
            "total liabilities and equity",
        ],
        # Equity
        "total equity": [
            "total shareholders' equity",
            "total shareholders equity",
            "shareholders' equity",
            "equity, total",
            "total equity and liabilities",
        ],
        # Cash flow
        "net cash from operating activities": [
            "cash from operating activities",
            "cash provided by operating activities",
            "operating cash flow",
        ],
        "net cash from investing activities": [
            "cash from investing activities",
            "cash provided by investing activities",
            "investing cash flow",
        ],
        "net cash from financing activities": [
            "cash from financing activities",
            "cash provided by financing activities",
            "financing cash flow",
        ],
    }

    @classmethod
    def normalize_name(cls, name: str) -> str:
        """Normalize a line item name using synonyms.

        Args:
            name: Original line item name.

        Returns:
            Normalized name (canonical form if synonym found, else original).
        """
        name_lower = name.lower().strip()

        # Check if name matches any synonym
        for canonical, synonyms in cls.SYNONYMS.items():
            if name_lower == canonical.lower():
                return canonical

            # Check if name matches any synonym variation
            for synonym in synonyms:
                if name_lower == synonym.lower():
                    return canonical

        # No match found, return original
        return name

    @classmethod
    def is_synonym(cls, name1: str, name2: str) -> bool:
        """Check if two names are synonyms.

        Args:
            name1: First name.
            name2: Second name.

        Returns:
            True if names are synonyms.
        """
        normalized1 = cls.normalize_name(name1)
        normalized2 = cls.normalize_name(name2)

        return normalized1 == normalized2 and normalized1 != name1.lower()
