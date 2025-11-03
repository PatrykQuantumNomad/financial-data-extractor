"""
Restatement detection and priority logic.

Handles the priority of restated data from newer reports over older values.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class RestatementHandler:
    """Handle restatement priority and data lineage."""

    def prioritize_restated_data(
        self,
        extractions: list[dict[str, Any]],
    ) -> dict[str, dict[str, dict[str, Any]]]:
        """Prioritize restated data from newer reports.

        Strategy: Newer reports contain historical years that supersede older reports.
        Example: 2024 report shows 2022-2024 data -> use this over individual 2022, 2023 reports.

        Args:
            extractions: List of extraction records with 'raw_data' and fiscal_year.

        Returns:
            Dictionary mapping:
            {
                year: {
                    line_item_name: {
                        "value": value,
                        "source_fiscal_year": source fiscal year,
                        "restated": True/False,
                        "source_document_id": document_id
                    }
                }
            }
        """
        # Sort extractions by fiscal_year descending (newest first)
        sorted_extractions = sorted(
            extractions,
            key=lambda x: x.get("fiscal_year", 0) or x.get("raw_data", {}).get("fiscal_year", 0),
            reverse=True,
        )

        # Build map: year -> line_item -> best value
        year_line_item_map: dict[str, dict[str, dict[str, Any]]] = {}

        for extraction in sorted_extractions:
            fiscal_year = (
                extraction.get("fiscal_year")
                or extraction.get("raw_data", {}).get("fiscal_year")
                or 0
            )
            raw_data = extraction.get("raw_data", {})
            line_items = raw_data.get("line_items", [])
            document_id = extraction.get("document_id")

            for item in line_items:
                # Handle both formats: item_name (from our models) or name (legacy)
                item_name = item.get("item_name", "") or item.get("name", "")
                if not item_name:
                    continue

                values = item.get("value", {})
                if not isinstance(values, dict):
                    continue

                # For each year in the item's values
                for year_str, value in values.items():
                    if value is None:
                        continue

                    year = str(year_str)

                    # Initialize year if needed
                    if year not in year_line_item_map:
                        year_line_item_map[year] = {}

                    # Initialize line item if needed
                    if item_name not in year_line_item_map[year]:
                        year_line_item_map[year][item_name] = {}

                    # Check if we already have a value for this year+line_item
                    existing = year_line_item_map[year].get(item_name)

                    # Use this value if:
                    # 1. No existing value, OR
                    # 2. This extraction's fiscal_year is newer than existing source
                    should_use = False
                    is_restated = False

                    # Determine if this is restated data (fiscal year > data year)
                    if year.isdigit():
                        is_restated = fiscal_year > int(year)

                    if not existing:
                        should_use = True
                    else:
                        existing_source_year = existing.get("source_fiscal_year", 0)
                        # If this extraction's fiscal year is newer, it takes precedence
                        if fiscal_year > existing_source_year:
                            should_use = True

                    if should_use:
                        year_line_item_map[year][item_name] = {
                            "value": value,
                            "source_fiscal_year": fiscal_year,
                            "restated": is_restated,
                            "source_document_id": document_id,
                            "source_extraction_id": extraction.get("id"),
                        }

        logger.info(
            f"Prioritized restated data: {len(year_line_item_map)} years, "
            f"{sum(len(items) for items in year_line_item_map.values())} line items"
        )

        return year_line_item_map
