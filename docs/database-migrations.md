---
layout: default
title: Database Migrations
description: Alembic migration commands, workflow, and best practices for database schema changes
nav_order: 5
---

# Database Migrations

This guide covers using Alembic for database migrations, including common commands, workflows, and best practices.

## About Alembic

### What is Alembic?

[Alembic](https://alembic.sqlalchemy.org/) is a database migration tool for SQLAlchemy. It provides:

- **Version Control for Database Schema**: Track all database schema changes over time
- **Automated Migration Generation**: Detect changes between SQLAlchemy models and generate migrations
- **Reproducible Deployments**: Apply the same schema changes across development, staging, and production
- **Rollback Capability**: Safely downgrade to previous schema versions when needed

### Why Alembic in This Project?

Alembic is used in the Financial Data Extractor project to:

1. **Manage Schema Evolution**: As the project evolves, database schema changes are version-controlled and traceable
2. **Enable Team Collaboration**: All developers can apply the same migrations to their local databases
3. **Support Data Migrations**: Not just schema changes, but also data transformations (e.g., seeding initial companies)
4. **Ensure Consistency**: The same migration process works across all environments (development, CI/CD, production)

### How Alembic Works in This Project

**Configuration:**

- **Alembic Config**: `backend/alembic.ini` - Contains database connection settings and migration directory paths
- **Migration Environment**: `backend/alembic/env.py` - Handles database connection and migration execution
- **Migrations Directory**: `backend/alembic/versions/` - Contains all migration files

**Workflow:**

1. **Model Changes**: When you modify SQLAlchemy models in `app/db/models/`, Alembic can detect the changes
2. **Generate Migration**: Run `make migrate-create NAME="description"` to auto-generate a migration file
3. **Review Migration**: Always review the generated migration file before applying
4. **Apply Migration**: Run `make migrate` to apply migrations to your database
5. **Version Tracking**: Alembic tracks applied migrations in the `alembic_version` table

**Integration with SQLAlchemy:**

- Alembic reads from SQLAlchemy models defined in `app/db/models/` via `Base.metadata` in `app/db/base.py`
- The `alembic/env.py` imports all models to enable auto-detection of schema changes
- Uses the same database connection configuration as the FastAPI application
- Supports both declarative SQLAlchemy models and raw SQL operations via `op.execute()`

**Connection Configuration:**

Alembic reads database connection settings from (in priority order):

1. `DATABASE_URL` environment variable (highest priority)
2. Settings from `config.py` (reads from `.env` file using Pydantic Settings)
3. Default values in `alembic.ini` (fallback)

This allows flexible configuration across different environments while maintaining consistency.

## Quick Start

```bash
# Apply all migrations
cd backend
make migrate

# Check migration status
make migrate-history

# Verify database setup
make db-info
make db-list-companies
```

## Backend Database Makefile Commands

All database migration operations are managed through the Makefile in the `backend/` directory:

```bash
cd backend

# Migration Commands
make migrate            # Apply all migrations (alias for migrate-up)
make migrate-up         # Apply all migrations
make migrate-down       # Rollback last migration
make migrate-create NAME="description"  # Create new migration
make migrate-history    # Show migration history

# Database Utilities
make db-reset           # Reset database (WARNING: destructive)
make db-list-companies  # List all companies (uses db_manager.py)
make db-info            # Show database info (uses db_manager.py)
```

## Common Migration Commands

### Apply All Migrations

```bash
# Using Makefile (recommended)
cd backend
make migrate

# Or directly with alembic
alembic upgrade head
```

### Check Current Migration Status

```bash
# Using Makefile
cd backend
make migrate-history

# Or directly with alembic
alembic current
```

### View Migration History

```bash
# Using Makefile
cd backend
make migrate-history

# Or with verbose output
alembic history --verbose
```

### Create a New Migration (Auto-generate)

Alembic will detect changes in your models and generate migration:

```bash
# Using Makefile (from backend/)
cd backend
make migrate-create NAME="description of changes"

# Or directly with alembic
alembic revision --autogenerate -m "description of changes"
```

**Note:** Always review auto-generated migrations before applying!

### Create a Blank Migration

For data migrations or complex schema changes:

```bash
# From backend/
cd backend
alembic revision -m "description of changes"
```

Edit the generated file in `backend/alembic/versions/` directory, then apply with `make migrate`.

### Upgrade to Specific Version

```bash
# Upgrade to a specific revision
cd backend
alembic upgrade <revision_id>

# Upgrade by relative number
alembic upgrade +1  # Upgrade one version
alembic upgrade +2  # Upgrade two versions
```

### Downgrade Database

```bash
# Downgrade to previous version (using Makefile)
cd backend
make migrate-down

# Or directly with alembic
alembic downgrade -1

# Downgrade to specific version
alembic downgrade <revision_id>

# Downgrade to base (empty database)
alembic downgrade base
```

### View SQL Without Executing

Preview what SQL would be executed:

```bash
# See what SQL would be run
cd backend
alembic upgrade head --sql
```

## Migration Files

All migration files are stored in `backend/alembic/versions/` with the format:

```text
<revision_id>_<description>.py
```

### Migration File Structure

Each migration file contains:

- **Revision ID**: Unique identifier (e.g., `001`, `002`)
- **Description**: Human-readable description of the migration
- **Upgrade Function**: SQLAlchemy operations to apply the migration
- **Downgrade Function**: SQLAlchemy operations to rollback the migration
- **Dependencies**: Links to previous migrations in the chain

**Example Migration Structure:**

```python
"""Add user email column

Revision ID: 003
Revises: 002
Create Date: 2025-02-01 10:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('companies', sa.Column('email', sa.String(), nullable=True))

def downgrade():
    op.drop_column('companies', 'email')
```

### Current Migrations

1. **001_create_initial_schema.py** - Creates all core tables:

   - `companies` - Company information (name, primary_ticker, tickers JSONB, IR URL)
   - `documents` - PDF documents (annual reports)
   - `extractions` - Raw LLM extractions (JSONB)
   - `compiled_statements` - Compiled 10-year views (JSONB)

2. **002_seed_initial_companies.py** - Seeds initial companies:

   - **AstraZeneca PLC** - Tickers: AZN (LSE, NASDAQ)
   - **SAP SE** - Tickers: SAP (XETRA, NYSE)
   - **Siemens AG** - Tickers: SIE (XETRA)
   - **ASML Holding N.V.** - Tickers: ASML (Euronext Amsterdam, NASDAQ)
   - **Unilever PLC** - Tickers: ULVR (LSE), UNA (Euronext Amsterdam), UL (NYSE)
   - **Allianz SE** - Tickers: ALV (XETRA)

   All companies include their Investor Relations URLs for annual report access.

## Verify Database Setup

After running migrations, verify everything is set up correctly:

```bash
# Option 1: Show database info (migration status + company count)
cd backend
make db-info

# Option 2: List all seeded companies with details
make db-list-companies

# Option 3: Check migration status directly
alembic current

# Option 4: Connect via psql (using Infrastructure Makefile)
cd ../infrastructure
make psql
# Then run: SELECT COUNT(*) FROM companies;
```

**Expected Output:** You should see 6 companies (AstraZeneca, SAP, Siemens, ASML, Unilever, Allianz) after running migration `002_seed_initial_companies.py`.

## Troubleshooting

### Migration Out of Sync

If your database schema doesn't match Alembic's version:

```bash
# Check current version
cd backend
alembic current

# View history
alembic history

# Stamp database at current state (without running migrations)
# Use with caution - only if database matches expected schema
alembic stamp head
```

### Reset Database

**⚠️ WARNING: This will destroy all data!**

```bash
# Drop all tables and re-run migrations (using Makefile)
cd backend
make db-reset

# Or manually:
alembic downgrade base
alembic upgrade head
```

### Connection Issues

```bash
# Option 1: Test database connection and show info (from backend/)
cd backend
make db-info

# Option 2: Connect via psql using Infrastructure Makefile (from infrastructure/)
cd infrastructure
make psql

# Option 3: View service URLs and connection strings
make url

# Option 4: Test Python connection
cd ../backend
python -c "from app.db.base import engine; print(engine.connect())"
```

### Generate Migration but Don't Auto-detect

```bash
# Create empty migration template
cd backend
alembic revision -m "manual changes"

# Edit the generated file in alembic/versions/ directory
# Then apply:
alembic upgrade head
```

## Best Practices

1. **Always review auto-generated migrations** before applying
2. **Test migrations on development database first**
3. **Never edit applied migrations** - create new ones instead
4. **Use descriptive migration messages** (e.g., `make migrate-create NAME="add_user_email_index"`)
5. **Keep migrations small and focused** - one logical change per migration
6. **Add indexes for foreign keys and frequently queried columns**
7. **Use transactions** - Alembic wraps each migration in a transaction automatically

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

### Docker Container Startup

When running the backend as a Docker service, migrations should run automatically:

```yaml
backend:
  command: >
    sh -c "alembic upgrade head && 
           uvicorn app.main:app --host 0.0.0.0 --port 8000"
```

This ensures migrations run before the app starts.

## Manual Migration in Docker Environment

If you need to run migrations manually:

```bash
# Option 1: Using Makefiles (recommended)
# Start database services
cd infrastructure
make up-dev

# Apply migrations
cd ../backend
make migrate

# Option 2: Check database is ready first
cd infrastructure
make health
make url  # View connection details

# Option 3: From inside backend container (if running as Docker service)
docker exec -it <backend-container-name> alembic upgrade head
```

## Related Documentation

- **[Infrastructure Development Setup](infrastructure-development)** - Setting up Docker services
- **[Database Schema](database-schema)** - Understanding table structures
- **[Database Queries](database-queries)** - Useful SQL query examples
