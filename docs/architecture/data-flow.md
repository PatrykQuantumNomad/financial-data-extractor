---
layout: default
title: Data Flow
description: Detailed workflow from scraping to compilation
nav_order: 2
parent: Architecture Overview
---

# Data Flow

The Financial Data Extractor processes financial data through three main phases:

## Phase 1: Scraping & Classification

1. User initiates extraction for a company
2. FastAPI creates job record → sends to Celery
3. Worker 1 scrapes investor relations website
4. Identifies all PDFs (annual reports, presentations, etc.)
5. Classifies documents by type using:
   - Filename patterns
   - Document metadata
   - Content sampling
6. Stores PDFs in MinIO object storage
7. Creates database records for each PDF with metadata

### Scraping Process

The scraping worker uses **Crawl4AI** with LLM assistance to:
- Navigate investor relations websites
- Discover PDF links
- Classify documents (Annual Report, Quarterly Report, Presentation, etc.)
- Extract metadata (fiscal year, publication date)

### Document Classification

Documents are classified using multiple strategies:
1. **Filename Patterns**: "annual-report-2023.pdf" → Annual Report
2. **URL Patterns**: "/annual-reports/" → Annual Report
3. **Content Analysis**: LLM samples document content to determine type
4. **Metadata**: Publication dates, document titles

## Phase 2: Parsing & Extraction

1. For each Annual Report PDF:
2. Worker 2 extracts text/tables using:
   - PyMuPDF / pdfplumber for structured tables
   - OCR (Tesseract/AWS Textract) for scanned documents
3. Sends extracted content + prompt to LLM (via OpenRouter):
   - "Extract Income Statement, Balance Sheet, Cash Flow Statement"
   - "Return as structured JSON with all line items"
4. LLM returns structured financial data
5. Validates data structure and completeness
6. Stores raw extraction in database (JSON column)

### PDF Processing

**Structured PDFs:**
- PyMuPDF extracts tables directly
- pdfplumber extracts text with layout information
- Tables are converted to structured data

**Scanned PDFs:**
- OCR engine extracts text
- Layout analysis identifies table structures
- Text is sent to LLM for extraction

### LLM Extraction

The extraction process:
1. **Preprocessing**: Extract relevant sections (find financial statements)
2. **Prompt Engineering**: Detailed prompts with examples and constraints
3. **LLM Call**: Send to OpenRouter with structured output format
4. **Validation**: Verify JSON structure and required fields
5. **Storage**: Save raw extraction with metadata

### Extraction Metadata

Each extraction includes:
- **Confidence Score**: How certain the extraction is
- **Model Used**: Which LLM model was used
- **Tokens Used**: Cost tracking
- **Processing Time**: Performance metrics
- **Data Lineage**: Source document information

## Phase 3: Normalization & Compilation

1. For each statement type across all years:
2. Collect all line items from all reports
3. Normalize line item names:
   - "Revenue" vs "Total Revenue" vs "Revenues"
   - Apply fuzzy matching + manual mappings
4. Detect restated data:
   - 2024 report contains 2022, 2023 data → use this over 2022, 2023 reports
5. Build unified table with 10 years of columns
6. Fill in data prioritizing latest sources
7. Store compiled view in database
8. Generate metadata:
   - Data lineage (which report each value came from)
   - Confidence scores
   - Gaps or inconsistencies

### Line Item Normalization

**Fuzzy Matching:**
- Uses rapidfuzz library for string similarity
- Groups similar line items (e.g., "Revenue", "Revenues", "Total Revenue")
- Configurable similarity threshold

**Manual Mappings:**
- User-defined overrides for specific mappings
- Priority over fuzzy matching
- Company-specific mappings

**Restatement Detection:**
- Newer reports often contain restated historical data
- System detects and prioritizes restated values
- Maintains data lineage for audit trail

### Compilation Process

1. **Collect**: Gather all extractions for a company and statement type
2. **Normalize**: Apply fuzzy matching and manual mappings
3. **Merge**: Combine line items across all years
4. **Prioritize**: Use latest sources for each value
5. **Validate**: Check for consistency and completeness
6. **Store**: Save compiled statement with metadata

### Compiled Statement Structure

```json
{
  "company_id": 1,
  "statement_type": "Income Statement",
  "data": {
    "line_items": [
      {
        "name": "Revenue",
        "years": {
          "2015": 1000000,
          "2016": 1100000,
          ...
        },
        "metadata": {
          "sources": {
            "2015": "document_5",
            "2016": "document_6"
          },
          "confidence": {
            "2015": 0.95,
            "2016": 0.98
          }
        }
      }
    ]
  }
}
```

## Error Handling & Retries

### Scraping Errors
- Network timeouts → Retry with exponential backoff
- Rate limiting → Wait and retry
- Invalid URLs → Log and skip

### Extraction Errors
- LLM API errors → Retry up to 3 times
- Invalid JSON → Log error, mark extraction as failed
- Timeout → Retry with longer timeout

### Compilation Errors
- Missing data → Mark as gap, continue compilation
- Inconsistent data → Flag for manual review
- Validation errors → Log and skip invalid entries

## Performance Considerations

### Caching
- Redis caches frequently accessed data
- PDF content cached after first extraction
- Compiled statements cached for fast retrieval

### Parallelization
- Multiple Celery workers process tasks in parallel
- Document processing can be parallelized
- Statement compilation parallelized by statement type

### Optimization
- LLM responses cached to avoid duplicate extractions
- Incremental compilation (only recompile changed statements)
- Database indexes for fast queries

## Data Quality

### Validation Steps
1. **Schema Validation**: Verify JSON structure matches expected schema
2. **Business Logic Validation**: Check calculations (e.g., Assets = Liabilities + Equity)
3. **Consistency Checks**: Compare values across years for anomalies
4. **Completeness Checks**: Verify required fields are present

### Quality Metrics
- **Confidence Scores**: Per-extraction and per-value confidence
- **Coverage**: Percentage of expected line items extracted
- **Accuracy**: Manual verification results (when available)
- **Consistency**: Variance in values across reports

## Related Documentation

- **[Technology Decisions](technology-decisions.html)** - Why we chose each component
- **[Task Processing](../infrastructure/tasks.html)** - Celery task system details
- **[Database Schema](../database/schema.html)** - Data storage structure
