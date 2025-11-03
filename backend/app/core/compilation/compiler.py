"""
Statement compiler for multi-year financial statement compilation.

Combines normalized line items across years with restatement priority.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

import logging
from typing import Any

from app.core.compilation.restatement import RestatementHandler

logger = logging.getLogger(__name__)


class StatementCompiler:
    """Compile multi-year financial statements from normalized data."""

    def __init__(self):
        """Initialize compiler."""
        self.restatement_handler = RestatementHandler()

    def compile_statement(
        self,
        normalized_map: dict[str, dict[str, Any]],
        prioritized_data: dict[str, dict[str, dict[str, Any]]],
        statement_type: str,
        currency: str = "EUR",
        unit: str = "thousands",
    ) -> dict[str, Any]:
        """Compile multi-year statement from normalized and prioritized data.

        Args:
            normalized_map: Normalized line items mapping from LineItemNormalizer.
            prioritized_data: Prioritized data from RestatementHandler.
            statement_type: Type of statement.
            currency: Currency code.
            unit: Unit (thousands, millions, etc.).

        Returns:
            Compiled statement data in format expected by frontend:
            {
                "lineItems": [...],
                "years": [...],
                "currency": "...",
                "unit": "...",
                "metadata": {...}
            }
        """
        # Get all years from prioritized data
        years = sorted(
            [int(year) for year in prioritized_data.keys() if year.isdigit()],
            reverse=True,
        )

        if not years:
            logger.warning("No years found in prioritized data")
            return {
                "lineItems": [],
                "years": [],
                "currency": currency,
                "unit": unit,
                "metadata": {"line_item_count": 0},
            }

        # Build line items array
        line_items = []

        for canonical_name, normalized_entry in normalized_map.items():
            line_item: dict[str, Any] = {
                "name": canonical_name,
                "level": normalized_entry.get("variations", [{}])[0].get(
                    "indentation_level", 0
                ),
                "isTotal": False,  # Will be set based on original data
            }

            # Add values for each year
            for year in years:
                year_str = str(year)

                # Get value from prioritized data
                year_data = prioritized_data.get(year_str, {})
                item_data = year_data.get(canonical_name)

                if item_data:
                    line_item[year_str] = item_data.get("value")
                    # Store restated flag (optional, for frontend display)
                    if item_data.get("restated"):
                        line_item[f"{year_str}_restated"] = True
                else:
                    line_item[year_str] = None

            line_items.append(line_item)

        # Sort line items by typical financial statement order
        # (This could be enhanced with a predefined order mapping)
        line_items_sorted = self._sort_line_items(line_items, statement_type)

        compiled_data = {
            "lineItems": line_items_sorted,
            "years": [str(year) for year in years],
            "currency": currency,
            "unit": unit,
            "metadata": {
                "line_item_count": len(line_items_sorted),
                "year_count": len(years),
                "statement_type": statement_type,
            },
        }

        logger.info(
            f"Compiled {statement_type}: {len(line_items_sorted)} line items, "
            f"{len(years)} years"
        )

        return compiled_data

    def _sort_line_items(
        self, line_items: list[dict[str, Any]], statement_type: str
    ) -> list[dict[str, Any]]:
        """Sort line items in typical financial statement order.

        Args:
            line_items: List of line item dictionaries.
            statement_type: Type of statement.

        Returns:
            Sorted list of line items.
        """
        # Simple sorting: by level first, then by typical order keywords
        # This is a basic implementation - could be enhanced with predefined order

        def get_sort_key(item: dict[str, Any]) -> tuple[int, str]:
            level = item.get("level", 0)
            name = item.get("name", "").lower()

            # Priority keywords (earlier = higher priority)
            priority_keywords = {
                "revenue": 1,
                "sales": 1,
                "cost": 2,
                "gross": 3,
                "operating": 4,
                "income": 5,
                "profit": 5,
                "net": 6,
                "assets": 1,
                "liabilities": 2,
                "equity": 3,
            }

            priority = 999
            for keyword, prio in priority_keywords.items():
                if keyword in name:
                    priority = prio
                    break

            return (level, priority, name)

        return sorted(line_items, key=get_sort_key)
