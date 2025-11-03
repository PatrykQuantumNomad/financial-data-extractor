"""
Financial statement extractor using hybrid approach (tables + LLM).

Extracts financial data from PDFs using table extraction first,
then LLM for gaps and validation.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

import json
import logging
from typing import Any

from app.core.llm.client import OpenRouterClient
from app.core.llm.models import ExtractionMetadata, FinancialLineItem, FinancialStatementExtraction
from app.core.llm.prompts import SYSTEM_PROMPT, get_prompt_for_statement_type

logger = logging.getLogger(__name__)


class FinancialStatementExtractor:
    """Extract financial statements using hybrid approach (tables + LLM)."""

    def __init__(
        self,
        openrouter_client: OpenRouterClient,
        model: str = "openai/gpt-4o",
    ):
        """Initialize extractor.

        Args:
            openrouter_client: OpenRouter client instance.
            model: Model to use for extraction (default: gpt-4o).
        """
        self.client = openrouter_client
        self.model = model

    async def extract_statement(
        self,
        extracted_content: dict[str, Any],
        statement_type: str,
        company_name: str,
        fiscal_year: int,
        fiscal_year_end: str | None = None,
    ) -> FinancialStatementExtraction:
        """Extract a financial statement from extracted PDF content.

        Args:
            extracted_content: Dictionary with 'text', 'tables', 'financial_tables'.
            statement_type: Type of statement (income_statement, balance_sheet, cash_flow_statement).
            company_name: Company name for validation.
            fiscal_year: Primary fiscal year.
            fiscal_year_end: Fiscal year end date (default: YYYY-12-31).

        Returns:
            FinancialStatementExtraction with structured data.

        Raises:
            ValueError: If extraction fails or response is invalid.
        """
        if fiscal_year_end is None:
            fiscal_year_end = f"{fiscal_year}-12-31"

        # Try hybrid approach: tables first, then LLM
        # For now, we'll use LLM primarily but can enhance with table extraction later
        logger.info(f"Extracting {statement_type} for {company_name} (fiscal year {fiscal_year})")

        # Preprocess text for this statement type
        from app.core.pdf.preprocessor import PDFPreprocessor

        preprocessor = PDFPreprocessor()
        preprocessed_text = preprocessor.preprocess_for_statement(extracted_content, statement_type)

        # Log preprocessed text sample for debugging
        preprocessed_sample = preprocessed_text[:2000] if len(preprocessed_text) > 2000 else preprocessed_text
        logger.info(
            f"Preprocessed text sample for {statement_type} ({len(preprocessed_text)} chars):\n"
            f"{preprocessed_sample}...",
        )

        # Build prompt
        prompt = get_prompt_for_statement_type(statement_type, preprocessed_text)

        # Prepare messages
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]

        # Call LLM
        import time

        start_time = time.time()
        try:
            response = await self.client.create_completion(
                messages=messages,
                model=self.model,
                temperature=0.0,
                max_tokens=8000,
                response_format={"type": "json_object"},
            )

            elapsed_time = time.time() - start_time

            # Parse response
            content = response.get("content", "")
            if not content:
                raise ValueError("Empty response from LLM")

            try:
                response_data = json.loads(content)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse LLM response as JSON: {e}")
                logger.debug(f"Response content (first 1000 chars): {content[:1000]}")
                raise ValueError(f"Invalid JSON response from LLM: {e}") from e

            # Log raw response for debugging
            line_items_raw = response_data.get("line_items")
            line_items_count = len(line_items_raw) if line_items_raw is not None else 0

            if line_items_count == 0:
                # When line_items is empty, log more details at INFO level
                logger.warning(
                    f"LLM returned empty line_items for {statement_type}. "
                    f"Response keys: {list(response_data.keys())}, "
                    f"line_items type: {type(line_items_raw)}, "
                    f"line_items value: {line_items_raw}"
                )
                # Log full response structure for debugging (truncated to avoid huge logs)
                response_str = json.dumps(response_data, indent=2)
                if len(response_str) > 3000:
                    logger.debug(f"Full LLM response (truncated):\n{response_str[:3000]}...")
                else:
                    logger.debug(f"Full LLM response:\n{response_str}")
            else:
                logger.debug(
                    f"LLM response keys: {list(response_data.keys())}, "
                    f"line_items type: {type(line_items_raw)}, "
                    f"line_items count: {line_items_count}"
                )

            # Convert to our model format
            extraction = self._parse_extraction_response(
                response_data,
                statement_type,
                company_name,
                fiscal_year,
                fiscal_year_end,
                response.get("usage", {}),
                elapsed_time,
            )

            # Validate extraction
            self._validate_extraction(extraction, fiscal_year)

            logger.info(
                f"Successfully extracted {statement_type}",
                extra={
                    "company": company_name,
                    "fiscal_year": fiscal_year,
                    "line_items": len(extraction.line_items),
                    "extraction_time": elapsed_time,
                    "quality_score": extraction.extraction_metadata.data_quality_score,
                },
            )

            return extraction

        except Exception as e:
            logger.error(f"Extraction failed: {e}", exc_info=True)
            raise

    def _parse_extraction_response(
        self,
        response_data: dict[str, Any],
        statement_type: str,
        company_name: str,
        fiscal_year: int,
        fiscal_year_end: str,
        usage: dict[str, Any],
        elapsed_time: float,
    ) -> FinancialStatementExtraction:
        """Parse LLM response into FinancialStatementExtraction model.

        Args:
            response_data: Parsed JSON from LLM.
            statement_type: Expected statement type.
            company_name: Company name.
            fiscal_year: Fiscal year.
            fiscal_year_end: Fiscal year end date.
            usage: Token usage information.
            elapsed_time: Extraction time in seconds.

        Returns:
            FinancialStatementExtraction instance.
        """
        # Extract line items - handle different possible formats
        # Handle case where line_items key exists but value is None
        line_items_data = response_data.get("line_items")
        if line_items_data is None:
            # Try alternative keys
            line_items_data = response_data.get("lineItems") or response_data.get("items")

        # Ensure we have a list (handle None or empty)
        if line_items_data is None:
            line_items_data = []
        elif not isinstance(line_items_data, list):
            logger.warning(
                f"line_items is not a list: {type(line_items_data)}, converting to empty list"
            )
            line_items_data = []

        if not line_items_data:
            logger.error(
                f"No line items found in extraction response. Response keys: {list(response_data.keys())}"
            )
            # Log the actual value of line_items for debugging
            raw_line_items = response_data.get("line_items")
            logger.error(f"line_items value: {raw_line_items} (type: {type(raw_line_items)})")

            # Log full response for debugging (truncated to avoid huge logs)
            response_str = json.dumps(response_data, indent=2)
            if len(response_str) > 5000:
                logger.error(f"Full LLM response (truncated):\n{response_str[:5000]}...")
            else:
                logger.error(f"Full LLM response:\n{response_str}")

            raise ValueError(
                "No line items found in extraction response. "
                f"Available keys: {list(response_data.keys())}, "
                f"line_items type: {type(raw_line_items)}, "
                f"line_items value: {raw_line_items}"
            )

        # Get default currency and unit from response level
        default_currency = response_data.get("currency") or "EUR"
        default_unit = response_data.get("unit") or "thousands"

        line_items = []
        for idx, item_data in enumerate(line_items_data):
            try:
                # Handle None values for unit and currency - provide defaults
                item_unit = item_data.get("unit")
                if item_unit is None:
                    item_unit = default_unit

                item_currency = item_data.get("currency")
                if item_currency is None:
                    item_currency = default_currency

                # Ensure value is a dict (handle None case)
                item_value = item_data.get("value")
                if item_value is None:
                    item_value = {}
                if not isinstance(item_value, dict):
                    logger.warning(
                        f"Line item {idx} has non-dict value: {type(item_value)}, converting to dict"
                    )
                    item_value = {}

                # Convert to FinancialLineItem
                line_item = FinancialLineItem(
                    item_name=item_data.get("item_name", "") or item_data.get("itemName", "") or "",
                    value=item_value,
                    currency=item_currency,
                    unit=item_unit,
                    indentation_level=item_data.get("indentation_level")
                    or item_data.get("indentationLevel")
                    or 0,
                    is_subtotal=item_data.get("is_subtotal")
                    or item_data.get("isSubtotal")
                    or False,
                    is_total=item_data.get("is_total") or item_data.get("isTotal") or False,
                    confidence=item_data.get("confidence", "high"),
                    footnote_refs=item_data.get("footnote_refs") or item_data.get("footnoteRefs"),
                )
                line_items.append(line_item)
            except Exception as e:
                logger.error(
                    f"Failed to parse line item {idx}: {e}. Item data: {item_data}",
                    exc_info=True,
                )
                # Skip this item but continue with others
                continue

        if not line_items:
            raise ValueError(
                "Failed to parse any line items from extraction response. "
                f"Attempted to parse {len(line_items_data)} items."
            )

        # Create extraction metadata
        metadata = ExtractionMetadata(
            page_numbers=response_data.get("extraction_metadata", {}).get("page_numbers", []),
            sections_found=response_data.get("extraction_metadata", {}).get("sections_found", []),
            data_quality_score=response_data.get("extraction_metadata", {}).get(
                "data_quality_score", 0.8
            ),
            extraction_method="llm",
            model_used=self.model,
            tokens_used=usage.get("total_tokens"),
            extraction_time_seconds=elapsed_time,
        )

        # Create extraction
        extraction = FinancialStatementExtraction(
            statement_type=statement_type,
            company_name=company_name,
            fiscal_year=fiscal_year,
            fiscal_year_end=fiscal_year_end,
            currency=response_data.get("currency", "EUR"),
            unit=response_data.get("unit", "thousands"),
            line_items=line_items,
            extraction_metadata=metadata,
        )

        return extraction

    def _validate_extraction(
        self, extraction: FinancialStatementExtraction, expected_fiscal_year: int
    ) -> None:
        """Validate extracted data for consistency and completeness.

        Args:
            extraction: Extracted financial statement.
            expected_fiscal_year: Expected fiscal year.

        Raises:
            ValueError: If validation fails.
        """
        # Check fiscal year matches
        try:
            fiscal_year_val = (
                extraction.fiscal_year_end.year
                if hasattr(extraction.fiscal_year_end, "year")
                else int(str(extraction.fiscal_year_end)[:4])
            )
        except Exception:
            fiscal_year_val = extraction.fiscal_year

        if fiscal_year_val != expected_fiscal_year:
            logger.warning(
                f"Fiscal year mismatch: expected {expected_fiscal_year}, got {fiscal_year_val}"
            )

        # Check for minimum line items
        min_items = {
            "income_statement": 10,
            "balance_sheet": 15,
            "cash_flow_statement": 10,
        }

        expected_min = min_items.get(extraction.statement_type, 5)
        if len(extraction.line_items) < expected_min:
            logger.warning(
                f"Low line item count: {len(extraction.line_items)} (expected >={expected_min})"
            )

        # Validate balance sheet equation
        if extraction.statement_type == "balance_sheet":
            self._validate_balance_sheet_equation(extraction)

    def _validate_balance_sheet_equation(self, extraction: FinancialStatementExtraction) -> None:
        """Validate: Assets = Liabilities + Equity.

        Args:
            extraction: Balance sheet extraction.
        """
        total_assets = None
        total_liabilities = None
        total_equity = None

        for item in extraction.line_items:
            name_lower = item.item_name.lower()
            if "total assets" in name_lower and item.is_total:
                total_assets = item.value
            elif "total liabilities" in name_lower and item.is_total:
                total_liabilities = item.value
            elif (
                "total equity" in name_lower or "total shareholders" in name_lower
            ) and item.is_total:
                total_equity = item.value

        # Validate equation for each year
        if total_assets and total_liabilities and total_equity:
            for year in total_assets.keys():
                assets = total_assets.get(year)
                liabilities = total_liabilities.get(year)
                equity = total_equity.get(year)

                if all(v is not None for v in [assets, liabilities, equity]):
                    # Allow 1% tolerance for rounding errors
                    expected = liabilities + equity
                    diff = abs(assets - expected)
                    tolerance = abs(expected * 0.01) if expected != 0 else 1

                    if diff > tolerance:
                        logger.warning(
                            f"Balance sheet equation doesn't balance for {year}: "
                            f"Assets={assets}, L+E={expected}, diff={diff}"
                        )
