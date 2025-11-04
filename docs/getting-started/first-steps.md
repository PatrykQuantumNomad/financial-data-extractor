---
layout: default
title: First Steps
description: Tutorial for your first financial data extraction
nav_order: 3
parent: Getting Started
---

# First Steps - Your First Extraction

This tutorial will guide you through extracting financial data for the first time.

## Prerequisites

- All services running (see [Installation Guide](installation.html))
- Backend API running on `http://localhost:3030`
- Celery worker running
- Frontend running on `http://localhost:3000`

## Step 1: View Companies

The system comes with 6 pre-seeded European companies:

1. AstraZeneca PLC (AZN)
2. SAP SE (SAP)
3. Siemens AG (SIE)
4. ASML Holding N.V. (ASML)
5. Unilever PLC (ULVR)
6. Allianz SE (ALV)

**Via Frontend:**
- Open http://localhost:3000
- Navigate to the Companies page
- You should see all 6 companies listed

**Via API:**
```bash
curl http://localhost:3030/api/v1/companies
```

## Step 2: Trigger Extraction

### Option A: Via Frontend

1. Select a company from the list (e.g., AstraZeneca)
2. Click "Extract Financial Data" button
3. Monitor the task status in the task monitor component

### Option B: Via API

```bash
# Trigger extraction for company ID 1 (AstraZeneca)
curl -X POST http://localhost:3030/api/v1/tasks/companies/1/extract

# Response:
# {
#   "task_id": "a00d8c65-c7fd-4360-8f4c-836b0df25f59",
#   "status": "PENDING",
#   "message": "Financial data extraction started for company 1"
# }
```

## Step 3: Monitor Progress

### Via Frontend

The task status monitor shows real-time progress:
- **Scraping** - Discovering PDFs from investor relations website
- **Classifying** - Categorizing documents
- **Downloading** - Fetching PDF files
- **Extracting** - Extracting financial statements using LLM
- **Compiling** - Normalizing and compiling statements

### Via API

```bash
# Check task status (replace TASK_ID with actual task ID)
curl http://localhost:3030/api/v1/tasks/TASK_ID

# Response:
# {
#   "task_id": "a00d8c65-c7fd-4360-8f4c-836b0df25f59",
#   "status": "SUCCESS",
#   "result": { ... },
#   "error": null
# }
```

### Via Flower Dashboard

1. Open http://localhost:5555
2. Navigate to "Tasks" tab
3. Find your task by ID or company name
4. View detailed execution timeline

## Step 4: View Results

### View Documents

**Via Frontend:**
- Navigate to the company's detail page
- Click "Documents" tab
- See all discovered annual reports

**Via API:**
```bash
# List documents for company 1
curl http://localhost:3030/api/v1/documents/companies/1
```

### View Extractions

**Via Frontend:**
- Navigate to the company's detail page
- Click "Extractions" tab
- See raw financial statement extractions

**Via API:**
```bash
# List extractions for a document
curl http://localhost:3030/api/v1/extractions/documents/DOCUMENT_ID
```

### View Compiled Statements

**Via Frontend:**
- Navigate to the company's detail page
- Click "Statements" tab
- Select statement type (Income Statement, Balance Sheet, Cash Flow)
- View 10-year compiled financial data

**Via API:**
```bash
# Get compiled income statement for company 1
curl http://localhost:3030/api/v1/compiled-statements/companies/1/statement-type/Income%20Statement
```

## Step 5: Understand the Data

### Compiled Statement Structure

Each compiled statement contains:
- **Line Items** - Normalized financial line items (e.g., "Revenue", "Total Assets")
- **Years** - Columns for each fiscal year (e.g., 2015-2024)
- **Values** - Financial values in the company's reporting currency
- **Metadata** - Data lineage, confidence scores, gaps

### Data Quality Indicators

- **Confidence Scores** - How certain the extraction is
- **Data Lineage** - Which report each value came from
- **Restatements** - Newer reports may contain restated historical data
- **Gaps** - Missing years or line items

## Common Tasks

### Extract Data for All Companies

```bash
# For each company, trigger extraction
for company_id in 1 2 3 4 5 6; do
  curl -X POST http://localhost:3030/api/v1/tasks/companies/$company_id/extract
done
```

### Recompile Statements

If you've added new extractions and want to recompile:

```bash
curl -X POST http://localhost:3030/api/v1/tasks/companies/1/recompile
```

### Download a PDF

```bash
# Get document info
curl http://localhost:3030/api/v1/documents/DOCUMENT_ID

# Download PDF from storage
curl "http://localhost:3030/api/v1/documents/storage/download?object_key=company_1/2023/annual_report.pdf" \
  --output document.pdf
```

## Next Steps

Now that you've completed your first extraction:

1. **[Explore the API](../api/reference.html)** - Learn all available endpoints
2. **[Understand the Architecture](../architecture/)** - Learn how the system works
3. **[Database Schema](../database/schema.html)** - Understand data structures
4. **[Task Processing](../infrastructure/tasks.html)** - Learn about Celery tasks

## Troubleshooting

**Extraction Takes Too Long:**
- Normal: Full extraction can take 10 minutes to 2 hours per company
- Check Celery worker logs for progress
- Monitor Flower dashboard for task status

**No Documents Found:**
- Check investor relations URL is correct
- Verify website is accessible
- Check scraping worker logs

**LLM Extraction Fails:**
- Verify OpenRouter API key is valid
- Check API credits/balance
- Review extraction worker logs

**Compilation Shows Missing Data:**
- Some years may not have reports
- Check document list for available fiscal years
- Verify extractions were successful

## Tips

- **Start Small**: Test with one company first
- **Monitor Resources**: Watch Docker container resources during extraction
- **Use Flower**: Flower dashboard provides excellent visibility into task execution
- **Check Logs**: Review worker logs for detailed execution information
- **Verify Data**: Always verify extracted data looks correct before trusting it
