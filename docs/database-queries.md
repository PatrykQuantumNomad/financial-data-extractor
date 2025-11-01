---
layout: default
title: Database Queries
description: Useful SQL queries for inspecting and querying financial data
nav_order: 5
---

# Database Queries

This guide provides useful SQL queries for inspecting and working with the financial data extractor database.

## Accessing the Database

### Using Makefile (Recommended)

```bash
# Connect via psql using Infrastructure Makefile
cd infrastructure
make psql
```

### Using db_manager.py

```bash
# List all companies
cd backend
make db-list-companies

# Show database info
make db-info
```

## Migration Queries

### Check Applied Migrations

```bash
# Using Makefile (from backend/)
cd backend
make migrate-history

# Or via SQL
cd ../infrastructure
make psql
# Then run: SELECT * FROM alembic_version;
```

```sql
SELECT * FROM alembic_version;
```

## Company Queries

### View All Companies

```bash
# Using Makefile (recommended)
cd backend
make db-list-companies
```

Or via SQL:

```sql
SELECT
    id,
    name,
    primary_ticker,
    tickers,
    ir_url,
    created_at
FROM companies
ORDER BY name;
```

### View All Companies with Ticker Details

```bash
# Using Makefile (recommended)
cd backend
make db-list-companies
```

Or via SQL:

```sql
SELECT
    c.id,
    c.name,
    c.primary_ticker,
    jsonb_array_elements(c.tickers) AS ticker_details,
    c.ir_url
FROM companies c
ORDER BY c.name;
```

### Query Companies by Ticker (Search All Exchanges)

Find company by any ticker symbol across all exchanges:

```sql
-- Option 1: Using primary_ticker or JSONB contains
SELECT
    c.id,
    c.name,
    c.primary_ticker,
    c.tickers,
    c.ir_url
FROM companies c
WHERE c.primary_ticker = 'AZN'
   OR c.tickers @> '[{"ticker": "AZN"}]'::jsonb
   OR EXISTS (
       SELECT 1
       FROM jsonb_array_elements(c.tickers) AS ticker_obj
       WHERE ticker_obj->>'ticker' = 'AZN'
   );
```

```sql
-- Option 2: Using jsonb_array_elements
SELECT
    c.id,
    c.name,
    c.primary_ticker,
    c.tickers,
    ticker_elem->>'ticker' as matching_ticker,
    ticker_elem->>'exchange' as exchange,
    c.ir_url
FROM companies c,
     jsonb_array_elements(c.tickers) AS ticker_elem
WHERE ticker_elem->>'ticker' = 'AZN';
```

### View All Tickers for a Company

```sql
SELECT
    c.name,
    c.primary_ticker,
    jsonb_array_elements(c.tickers) AS ticker_info
FROM companies c
WHERE c.name = 'Unilever PLC';
```

## Document Queries

### View All Documents

```sql
SELECT
    d.id,
    c.name as company_name,
    d.url,
    d.fiscal_year,
    d.document_type,
    d.file_path,
    d.created_at
FROM documents d
JOIN companies c ON c.id = d.company_id
ORDER BY c.name, d.fiscal_year DESC;
```

### Documents by Company

```sql
SELECT
    c.name,
    c.primary_ticker,
    d.fiscal_year,
    d.document_type,
    d.url,
    d.file_path
FROM companies c
JOIN documents d ON d.company_id = c.id
WHERE c.primary_ticker = 'AZN'
ORDER BY d.fiscal_year DESC;
```

## Extraction Queries

### View Extractions for a Company

```sql
SELECT
    c.name,
    c.primary_ticker,
    d.fiscal_year,
    d.document_type,
    e.statement_type,
    e.raw_data->>'currency' as currency,
    e.created_at as extraction_date
FROM companies c
JOIN documents d ON d.company_id = c.id
JOIN extractions e ON e.document_id = d.id
WHERE c.primary_ticker = 'AZN'
ORDER BY d.fiscal_year DESC, e.statement_type;
```

### Count Extractions per Company

```sql
SELECT
    c.name,
    c.primary_ticker,
    COUNT(e.id) as total_extractions,
    COUNT(DISTINCT d.fiscal_year) as years_with_data
FROM companies c
LEFT JOIN documents d ON d.company_id = c.id
LEFT JOIN extractions e ON e.document_id = d.id
GROUP BY c.id, c.name, c.primary_ticker
ORDER BY total_extractions DESC;
```

### View Extraction Details

```sql
SELECT
    e.id,
    c.name as company_name,
    d.fiscal_year,
    e.statement_type,
    jsonb_array_length(e.raw_data->'line_items') as num_line_items,
    e.raw_data->>'currency' as currency,
    e.created_at
FROM extractions e
JOIN documents d ON d.id = e.document_id
JOIN companies c ON c.id = d.company_id
ORDER BY e.created_at DESC
LIMIT 10;
```

## Compiled Statements Queries

### View Compiled Statement

```sql
SELECT
    c.name,
    c.primary_ticker,
    cs.statement_type,
    jsonb_array_length(cs.data->'line_items') as num_line_items,
    cs.data->>'currency' as currency,
    cs.updated_at
FROM companies c
JOIN compiled_statements cs ON cs.company_id = c.id
WHERE c.primary_ticker = 'AZN'
  AND cs.statement_type = 'income_statement';
```

### View All Compiled Statements Summary

```sql
SELECT
    c.name,
    c.primary_ticker,
    cs.statement_type,
    jsonb_array_length(cs.data->'line_items') as num_line_items,
    cs.updated_at,
    CASE
        WHEN cs.updated_at > NOW() - INTERVAL '7 days' THEN 'Recent'
        ELSE 'Stale'
    END as freshness
FROM companies c
JOIN compiled_statements cs ON cs.company_id = c.id
ORDER BY c.name, cs.statement_type;
```

### Get Line Items from Compiled Statement

```sql
SELECT
    c.name,
    cs.statement_type,
    jsonb_array_elements(cs.data->'line_items') AS line_item
FROM companies c
JOIN compiled_statements cs ON cs.company_id = c.id
WHERE c.primary_ticker = 'AZN'
  AND cs.statement_type = 'income_statement'
LIMIT 5;
```

## Statistics Queries

### Database Statistics

Get overview of database contents:

```sql
SELECT
    'Companies' as table_name,
    COUNT(*) as count
FROM companies
UNION ALL
SELECT
    'Documents',
    COUNT(*)
FROM documents
UNION ALL
SELECT
    'Extractions',
    COUNT(*)
FROM extractions
UNION ALL
SELECT
    'Compiled Statements',
    COUNT(*)
FROM compiled_statements;
```

### Companies with Most Documents

```sql
SELECT
    c.name,
    c.primary_ticker,
    COUNT(DISTINCT d.id) as document_count,
    MIN(d.fiscal_year) as earliest_year,
    MAX(d.fiscal_year) as latest_year,
    COUNT(DISTINCT e.id) as extraction_count
FROM companies c
LEFT JOIN documents d ON d.company_id = c.id
LEFT JOIN extractions e ON e.document_id = d.id
GROUP BY c.id, c.name, c.primary_ticker
ORDER BY document_count DESC;
```

### Statement Types Distribution

```sql
SELECT
    statement_type,
    COUNT(*) as count,
    COUNT(DISTINCT document_id) as document_count,
    COUNT(DISTINCT (
        SELECT company_id
        FROM documents
        WHERE id = extractions.document_id
    )) as company_count
FROM extractions
GROUP BY statement_type
ORDER BY count DESC;
```

## JSONB Queries

### Query JSONB Tickers

```sql
-- Find companies with ticker on specific exchange
SELECT
    c.name,
    c.primary_ticker,
    ticker_elem->>'ticker' as ticker,
    ticker_elem->>'exchange' as exchange
FROM companies c,
     jsonb_array_elements(c.tickers) AS ticker_elem
WHERE ticker_elem->>'exchange' = 'LSE';
```

### Extract Values from Extraction JSONB

```sql
-- Get revenue values from income statement extractions
SELECT
    c.name,
    d.fiscal_year,
    line_item->>'name' as line_item_name,
    line_item->'values'->>'2024' as value_2024
FROM companies c
JOIN documents d ON d.company_id = c.id
JOIN extractions e ON e.document_id = d.id,
     jsonb_array_elements(e.raw_data->'line_items') AS line_item
WHERE e.statement_type = 'income_statement'
  AND line_item->>'name' ILIKE '%revenue%'
ORDER BY c.name, d.fiscal_year DESC;
```

### Query Compiled Statement Data

```sql
-- Get all line items with their values
SELECT
    c.name,
    cs.statement_type,
    line_item->>'name' as line_item_name,
    line_item->'values' as year_values,
    line_item->>'is_total' as is_total
FROM companies c
JOIN compiled_statements cs ON cs.company_id = c.id,
     jsonb_array_elements(cs.data->'line_items') AS line_item
WHERE c.primary_ticker = 'AZN'
  AND cs.statement_type = 'income_statement'
ORDER BY (line_item->>'indentation_level')::int, line_item->>'name';
```

## Performance Queries

### Check Index Usage

```sql
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan as index_scans,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;
```

### Table Sizes

```sql
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
    pg_total_relation_size(schemaname||'.'||tablename) AS size_bytes
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## Related Documentation

- **[Infrastructure Development Setup](infrastructure-development)** - Setting up database access
- **[Database Schema](database-schema)** - Understanding table structures
- **[Database Migrations](database-migrations)** - Migration commands
