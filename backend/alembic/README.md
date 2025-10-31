# Database Migrations with Alembic

This directory contains database migration scripts managed by Alembic.

## Quick Start

### Apply All Migrations

```bash
# From the backend directory
alembic upgrade head
```

### Check Current Migration Status

```bash
alembic current
```

### View Migration History

```bash
alembic history --verbose
```

## Common Commands

### Create a New Migration (Auto-generate)

```bash
# Alembic will detect changes in your models and generate migration
alembic revision --autogenerate -m "description of changes"
```

### Create a Blank Migration

```bash
# For data migrations or complex schema changes
alembic revision -m "description of changes"
```

### Upgrade to Specific Version

```bash
# Upgrade to a specific revision
alembic upgrade <revision_id>

# Upgrade by relative number
alembic upgrade +1  # Upgrade one version
alembic upgrade +2  # Upgrade two versions
```

### Downgrade Database

```bash
# Downgrade to previous version
alembic downgrade -1

# Downgrade to specific version
alembic downgrade <revision_id>

# Downgrade to base (empty database)
alembic downgrade base
```

### View SQL Without Executing

```bash
# See what SQL would be run
alembic upgrade head --sql
```

## Migration Files

All migration files are stored in `alembic/versions/` with the format:

```bash
<revision_id>_<description>.py
```

### Current Migrations

1. **001_create_initial_schema.py** - Creates all core tables:

   - `companies` - Company information (name, ticker, IR URL)
   - `documents` - PDF documents (annual reports)
   - `extractions` - Raw LLM extractions (JSONB)
   - `compiled_statements` - Compiled 10-year views (JSONB)

2. **002_seed_initial_companies.py** - Seeds initial companies:
   - Adyen
   - Heineken

## Environment Configuration

### Using Environment Variables

```bash
# Set DATABASE_URL environment variable
export DATABASE_URL="postgresql://user:pass@localhost:5432/financial_data_extractor"
alembic upgrade head
```

### Using .env File

```bash
# In backend/.env
DATABASE_URL=postgresql://user:pass@localhost:5432/financial_data_extractor
```

The `env.py` file will automatically read from environment variables.

## Database Schema

### Tables Overview

```sql
-- Companies (source data)
companies
  - id (PK)
  - name
  - ticker (unique)
  - ir_url
  - created_at

-- Documents (downloaded PDFs)
documents
  - id (PK)
  - company_id (FK → companies.id)
  - url
  - fiscal_year
  - document_type ('annual_report', 'quarterly', etc.)
  - file_path
  - created_at

-- Extractions (raw LLM output)
extractions
  - id (PK)
  - document_id (FK → documents.id)
  - statement_type ('income_statement', 'balance_sheet', 'cash_flow_statement')
  - raw_data (JSONB)
  - created_at

-- Compiled Statements (final 10-year views)
compiled_statements
  - id (PK)
  - company_id (FK → companies.id)
  - statement_type
  - data (JSONB)
  - updated_at
  - UNIQUE(company_id, statement_type)
```

### Foreign Key Cascades

All foreign keys use `ON DELETE CASCADE`, meaning:

- Deleting a company → deletes all its documents and compiled statements
- Deleting a document → deletes all its extractions

## Working with JSONB Columns

### Extractions JSON Structure

```json
{
  "statement_type": "income_statement",
  "company_name": "Adyen",
  "fiscal_year": 2024,
  "currency": "EUR",
  "line_items": [
    {
      "name": "Total Revenue",
      "values": {
        "2024": 97690,
        "2023": 96773,
        "2022": 91462
      },
      "indentation_level": 0,
      "is_total": true
    }
  ]
}
```

### Compiled Statements JSON Structure

```json
{
  "statement_type": "income_statement",
  "company_name": "Adyen",
  "currency": "EUR",
  "line_items": [
    {
      "name": "Total Revenue",
      "values": {
        "2024": 97690,
        "2023": 96773,
        "2022": 91462,
        "2021": 53823,
        "2020": 31536
      },
      "indentation_level": 0,
      "is_total": true,
      "variants": ["Total Revenue", "Revenues", "Total revenues"]
    }
  ]
}
```

## Troubleshooting

### Migration Out of Sync

If your database schema doesn't match Alembic's version:

```bash
# Check current version
alembic current

# View history
alembic history

# Stamp database at current state (without running migrations)
alembic stamp head
```

### Reset Database

```bash
# Drop all tables and re-run migrations
alembic downgrade base
alembic upgrade head
```

### Connection Issues

```bash
# Test database connection
python -c "from app.db.base import engine; print(engine.connect())"
```

### Generate Migration but Don't Auto-detect

```bash
# Create empty migration template
alembic revision -m "manual changes"

# Edit the generated file in versions/ directory
# Then apply:
alembic upgrade head
```

## Best Practices

1. **Always review auto-generated migrations** before applying
2. **Test migrations on development database first**
3. **Never edit applied migrations** - create new ones instead
4. **Use descriptive migration messages**
5. **Keep migrations small and focused**
6. **Add indexes for foreign keys and frequently queried columns**
7. **Use transactions** - Alembic wraps each migration in a transaction

## Docker Setup

### In docker-compose.yml

```yaml
backend:
  command: >
    sh -c "alembic upgrade head && 
           uvicorn app.main:app --host 0.0.0.0 --port 8000"
```

This ensures migrations run before the app starts.

## CI/CD Integration

### GitHub Actions Example

```yaml
- name: Run database migrations
  run: |
    cd backend
    alembic upgrade head
  env:
    DATABASE_URL: ${{ secrets.DATABASE_URL }}
```

## Useful Queries

### Check Applied Migrations

```sql
SELECT * FROM alembic_version;
```

### View All Companies

```sql
SELECT * FROM companies;
```

### View Extractions for a Company

```sql
SELECT
    c.name,
    d.fiscal_year,
    e.statement_type,
    e.raw_data->>'currency' as currency
FROM companies c
JOIN documents d ON d.company_id = c.id
JOIN extractions e ON e.document_id = d.id
WHERE c.ticker = 'ADYEN';
```

### View Compiled Statement

```sql
SELECT
    c.name,
    cs.statement_type,
    jsonb_array_length(cs.data->'line_items') as num_line_items,
    cs.updated_at
FROM companies c
JOIN compiled_statements cs ON cs.company_id = c.id
WHERE c.ticker = 'ADYEN'
  AND cs.statement_type = 'income_statement';
```
