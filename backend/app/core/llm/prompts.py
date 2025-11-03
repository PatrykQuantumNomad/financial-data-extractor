"""
Prompt templates for LLM operations (scraping and financial extraction).

Provides centralized prompt templates and instructions for all LLM interactions.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

SYSTEM_PROMPT = """You are a financial data extraction expert. Your task is to extract structured financial statement data from annual report text with perfect accuracy.

CRITICAL RULES:
1. Extract ALL line items exactly as they appear in the document
2. Preserve the exact wording used by the company
3. Maintain the hierarchical structure (parent-child relationships)
4. Include all columns (multiple years if present)
5. Return null for missing values, never fabricate data
6. Preserve negative numbers with minus sign (not parentheses)
7. Extract numerical values without thousands separators
8. Note currency if specified
9. Capture footnote references if present

OUTPUT FORMAT:
Return valid JSON matching the exact schema provided. Do not include any text outside the JSON structure.

DATA QUALITY:
- Double-check all numbers
- Verify that subtotals equal sum of components
- Flag any anomalies or inconsistencies
- If uncertain about a value, mark confidence as "low"

EDGE CASES:
- If a line item has no value, use null
- If a calculation is shown (e.g., "2023 - 2022"), extract the result only
- If there are multiple currencies, note each currency per column
- If text is unclear or OCR quality is poor, mark confidence as "low"
"""

INCOME_STATEMENT_PROMPT_TEMPLATE = """Extract the Income Statement (also called Statement of Operations, Profit & Loss, or P&L) from the following financial document text.

The document may be an annual report, quarterly report, or interim statement. Extract the financial data regardless of the reporting period.

DOCUMENT TEXT:
{document_text}

EXTRACTION INSTRUCTIONS:
1. Identify the Income Statement section (may be labeled as Income Statement, Statement of Operations, P&L, Profit & Loss, etc.)
2. Extract ALL line items in order from top to bottom
3. If this is a quarterly/interim report, extract the data for the period shown
4. Common sections include:
   - Revenue / Sales / Turnover
   - Cost of Revenue / Cost of Sales
   - Gross Profit
   - Operating Expenses (R&D, SG&A, etc.)
   - Operating Income
   - Interest Income/Expense
   - Income Before Taxes
   - Tax Provision
   - Net Income
   - Earnings Per Share (EPS)
4. Preserve indentation levels (0=main item, 1=sub-item, 2=sub-sub-item)
5. Extract all year columns present
6. Note the currency and unit (thousands, millions, etc.)

EXPECTED JSON SCHEMA:
{{
  "statement_type": "income_statement",
  "year": 2024,
  "period_end": "2024-12-31",
  "currency": "EUR",
  "unit": "millions",
  "line_items": [
    {{
      "item_name": "Revenue",
      "value": {{
        "2024": 1000000,
        "2023": 950000,
        "2022": 900000
      }},
      "currency": "EUR",
      "unit": "millions",
      "indentation_level": 0,
      "is_subtotal": false,
      "is_total": false,
      "confidence": "high"
    }}
  ]
}}

Return ONLY valid JSON, no additional text or markdown.
"""

BALANCE_SHEET_PROMPT_TEMPLATE = """Extract the Balance Sheet (also called Statement of Financial Position) from the following financial document text.

The document may be an annual report, quarterly report, or interim statement. Extract the financial data regardless of the reporting period.

DOCUMENT TEXT:
{document_text}

EXTRACTION INSTRUCTIONS:
1. Identify the Balance Sheet section (may be labeled as Balance Sheet, Statement of Financial Position, etc.)
2. Extract ALL line items from:
   ASSETS:
   - Current Assets (Cash, Receivables, Inventory, etc.)
   - Non-Current Assets (PP&E, Intangibles, etc.)
   - Total Assets

   LIABILITIES:
   - Current Liabilities (Payables, Short-term debt, etc.)
   - Non-Current Liabilities (Long-term debt, etc.)
   - Total Liabilities

   EQUITY:
   - Share Capital
   - Retained Earnings
   - Other Equity Components
   - Total Equity

3. Verify: Total Assets = Total Liabilities + Total Equity
4. Extract all year columns present
5. Note the currency and unit

EXPECTED JSON SCHEMA:
{{
  "statement_type": "balance_sheet",
  "year": 2024,
  "period_end": "2024-12-31",
  "currency": "EUR",
  "unit": "millions",
  "line_items": [
    {{
      "item_name": "Total Assets",
      "value": {{"2024": 5000000, "2023": 4800000}},
      "currency": "EUR",
      "unit": "millions",
      "indentation_level": 0,
      "is_total": true,
      "confidence": "high"
    }}
  ]
}}

Return ONLY valid JSON, no additional text or markdown.
"""

CASH_FLOW_STATEMENT_PROMPT_TEMPLATE = """Extract the Cash Flow Statement (also called Statement of Cash Flows) from the following financial document text.

The document may be an annual report, quarterly report, or interim statement. Extract the financial data regardless of the reporting period.

DOCUMENT TEXT:
{document_text}

EXTRACTION INSTRUCTIONS:
1. Identify the Cash Flow Statement section (may be labeled as Cash Flow Statement, Statement of Cash Flows, etc.)
2. Extract ALL line items from three sections:

   OPERATING ACTIVITIES:
   - Net Income
   - Adjustments (Depreciation, Changes in Working Capital, etc.)
   - Net Cash from Operating Activities

   INVESTING ACTIVITIES:
   - Capital Expenditures
   - Acquisitions/Divestitures
   - Net Cash from Investing Activities

   FINANCING ACTIVITIES:
   - Debt Issuance/Repayment
   - Dividends Paid
   - Share Buybacks
   - Net Cash from Financing Activities

3. Calculate: Net Change in Cash = Operating + Investing + Financing
4. Extract all year columns present
5. Note the currency and unit

EXPECTED JSON SCHEMA:
{{
  "statement_type": "cash_flow_statement",
  "year": 2024,
  "period_end": "2024-12-31",
  "currency": "EUR",
  "unit": "millions",
  "line_items": [
    {{
      "item_name": "Net Cash from Operating Activities",
      "value": {{"2024": 150000, "2023": 140000}},
      "currency": "EUR",
      "unit": "millions",
      "indentation_level": 0,
      "is_total": false,
      "confidence": "high"
    }}
  ]
}}

Return ONLY valid JSON, no additional text or markdown.
"""


# Scraping prompts
PDF_DISCOVERY_INSTRUCTION = """Find ALL PDFs and PDF-related content on this page. Be thorough and check for multiple patterns.

SEARCH PATTERNS - Check for ALL of these:

1. DIRECT PDF LINKS:
- URLs ending in .pdf
- Links with 'pdf' in the path
- Example: https://example.com/report.pdf

2. SEPARATED DOWNLOAD LINKS:
- Content title in one place, PDF link separate (often to the right or below)
- Look for [PDF], [Download], [View PDF] badges/buttons near titles
- The title link and PDF link are DIFFERENT URLs
Example:
* Title: "Annual Report 2023" → https://example.com/reports/2023
* PDF Link: "[PDF]" → https://example.com/reports/2023/download.pdf
Extract BOTH URLs: primary_url = title link, download_url = PDF link

3. PDF VIEWER PAGES:
- URLs containing /pdf/, /viewer/, /reader/ in the path
- URLs with 'pdf' parameter: ?format=pdf, ?type=pdf
- Example: https://onlinelibrary.wiley.com/doi/pdf/10.1155/2021/8812542
- Example: https://example.com/viewer?doc=12345

4. DOWNLOAD BUTTONS/LINKS:
- Text containing: "Download", "PDF", "Get PDF", "View PDF", "Télécharger", "Herunterladen"
- Often styled as buttons or prominent links
- May have icons (download icon, PDF icon)

5. EMBEDDED PDFs:
- iframes, object, or embed tags pointing to PDFs
- Data URLs containing PDF content

6. JAVASCRIPT/DYNAMIC LINKS:
- onclick handlers that download PDFs
- data-url or data-href attributes with PDF paths
- API endpoints like /api/download?id=123

EXTRACTION RULES:

A. For each PDF found, determine:
- title: The name/description of the document
- primary_url: Main link (article page, product page, etc.)
- download_url: Direct PDF download link IF DIFFERENT from primary_url
- link_text: Actual text of the link/button (e.g., "[PDF] aaai.org", "Download Annual Report", "Q4 2023 Results")
- context: Nearby text that provides context (author, date, description)
- pdf_indicator: How you found it (see categories above)

B. CRITICAL - Handle separated links:
If a document title and its PDF download link are in different places:
- Set primary_url = the title's link (viewer/article page)
- Set download_url = the separate PDF download link
- Set link_text = the text of the PDF download link

Example from an investor relations page:
```
Annual Report 2023                    [PDF] [Excel]
Quarterly Results Q4 2023            Download PDF
```
Extract as:
{{
    "title": "Annual Report 2023",
    "primary_url": "https://example.com/investor/annual-report-2023",
    "download_url": "https://example.com/files/annual-report-2023.pdf",
    "link_text": "[PDF]",
    "pdf_indicator": "pdf_badge"
}}

C. Year extraction:
- Look in: title, URL, filename, surrounding text
- Formats: 2023, 2022-2023, FY2023, Q4 2023
- Extract the most recent/relevant year

Return empty array if no PDFs found.
"""


def get_prompt_for_statement_type(statement_type: str, document_text: str) -> str:
    """Get prompt for a specific statement type.

    Args:
        statement_type: Type of statement (income_statement, balance_sheet, cash_flow_statement).
        document_text: Extracted text from PDF.

    Returns:
        Formatted prompt string.
    """
    templates = {
        "income_statement": INCOME_STATEMENT_PROMPT_TEMPLATE,
        "balance_sheet": BALANCE_SHEET_PROMPT_TEMPLATE,
        "cash_flow_statement": CASH_FLOW_STATEMENT_PROMPT_TEMPLATE,
    }

    template = templates.get(statement_type)
    if not template:
        raise ValueError(f"Unknown statement type: {statement_type}")

    return template.format(document_text=document_text)
