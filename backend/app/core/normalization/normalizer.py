"""
Line item normalizer using fuzzy matching and synonyms.

Normalizes line item names across multiple extractions using:
1. Manual mappings (user-defined)
2. Synonym matching (exact)
3. Fuzzy matching (similarity-based)

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

import logging
from typing import Any

from rapidfuzz import fuzz

from app.core.normalization.synonyms import FinancialSynonyms

logger = logging.getLogger(__name__)


class LineItemNormalizer:
    """Normalize line item names across extractions."""

    def __init__(
        self,
        fuzzy_threshold: int = 85,
        manual_mappings: dict[str, str] | None = None,
    ):
        """Initialize normalizer.

        Args:
            fuzzy_threshold: Similarity threshold for fuzzy matching (0-100).
            manual_mappings: Manual mappings of original -> canonical names.
        """
        self.fuzzy_threshold = fuzzy_threshold
        self.manual_mappings = manual_mappings or {}

        # Build reverse lookup for synonyms
        self._synonym_map: dict[str, str] = {}
        for canonical, synonyms in FinancialSynonyms.SYNONYMS.items():
            self._synonym_map[canonical.lower()] = canonical
            for synonym in synonyms:
                self._synonym_map[synonym.lower()] = canonical

    def normalize_line_items(self, extractions: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
        """Normalize line items across multiple extractions.

        Args:
            extractions: List of extraction dictionaries with 'raw_data'.

        Returns:
            Dictionary mapping normalized names to:
            - canonical_name: Canonical line item name
            - variations: List of original names and their sources
            - confidence: Normalization confidence (high/medium/low)
        """
        # Step 1: Collect all unique line items
        all_line_items: dict[str, list[dict[str, Any]]] = {}

        for extraction in extractions:
            raw_data = extraction.get("raw_data", {})
            line_items = raw_data.get("line_items", [])

            for item in line_items:
                item_name = item.get("item_name", "") or item.get("name", "")
                if not item_name:
                    continue

                # Initialize if not seen
                if item_name not in all_line_items:
                    all_line_items[item_name] = []

                # Store with extraction context
                all_line_items[item_name].append(
                    {
                        "original_name": item_name,
                        "extraction_id": extraction.get("id"),
                        "document_id": extraction.get("document_id"),
                        "fiscal_year": extraction.get("fiscal_year"),
                    }
                )

        # Step 2: Normalize names
        normalized_map: dict[str, dict[str, Any]] = {}

        for original_name, occurrences in all_line_items.items():
            canonical_name = self._normalize_name(original_name, normalized_map)

            # Add to normalized map
            if canonical_name not in normalized_map:
                normalized_map[canonical_name] = {
                    "canonical_name": canonical_name,
                    "variations": [],
                    "confidence": "high",
                }

            # Add this variation
            normalized_map[canonical_name]["variations"].extend(occurrences)

        logger.info(
            f"Normalized {len(all_line_items)} unique line items "
            f"into {len(normalized_map)} canonical names"
        )

        return normalized_map

    def _normalize_name(self, name: str, existing_normalized: dict[str, dict[str, Any]]) -> str:
        """Normalize a single line item name.

        Strategy:
        1. Check manual mappings
        2. Check synonyms
        3. Fuzzy match against existing normalized names
        4. Use original if no match

        Args:
            name: Original line item name.
            existing_normalized: Dictionary of already normalized names.

        Returns:
            Canonical normalized name.
        """
        # Step 1: Check manual mappings
        if name in self.manual_mappings:
            return self.manual_mappings[name]

        # Step 2: Check synonyms
        synonym_normalized = FinancialSynonyms.normalize_name(name)
        if synonym_normalized.lower() != name.lower():
            # Found synonym, but check if it's already in normalized map
            if synonym_normalized in existing_normalized:
                return synonym_normalized
            # Not yet in map, but we'll use the canonical form
            name = synonym_normalized

        # Step 3: Fuzzy match against existing normalized names
        name_lower = name.lower()
        best_match = None
        best_score = 0

        for normalized_name in existing_normalized.keys():
            normalized_lower = normalized_name.lower()

            # Calculate similarity
            similarity = fuzz.ratio(name_lower, normalized_lower)

            if similarity > best_score and similarity >= self.fuzzy_threshold:
                best_score = similarity
                best_match = normalized_name

        # Use best match if found
        if best_match:
            logger.debug(f"Fuzzy matched '{name}' -> '{best_match}' (similarity: {best_score}%)")
            return best_match

        # Step 4: Use original (normalized) name
        return name

    def get_confidence_score(self, normalized_entry: dict[str, Any]) -> str:
        """Calculate confidence score for normalization.

        Args:
            normalized_entry: Entry from normalized_map.

        Returns:
            Confidence level (high/medium/low).
        """
        variations = normalized_entry.get("variations", [])
        unique_names = {var.get("original_name", "") for var in variations}

        # High confidence: single variation or all synonyms
        if len(unique_names) == 1:
            return "high"

        # Check if all are known synonyms
        all_synonyms = True
        for name in unique_names:
            normalized = FinancialSynonyms.normalize_name(name)
            if normalized.lower() == name.lower():
                all_synonyms = False
                break

        if all_synonyms:
            return "high"

        # Medium confidence: 2-3 variations, likely same item
        if len(unique_names) <= 3:
            return "medium"

        # Low confidence: many variations
        return "low"
