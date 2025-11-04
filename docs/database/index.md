---
layout: default
title: Database
description: Database schema, migrations, queries, and database operations
nav_order: 7
has_children: true
---

# Database Documentation

The Financial Data Extractor uses **PostgreSQL 16** as the primary database, storing company information, documents, financial statement extractions, and compiled statements.

## Database Overview

- **PostgreSQL 16** - Primary database
- **JSONB Support** - For storing flexible financial data structures
- **Alembic Migrations** - Schema version control
- **Connection Pooling** - Async connection pool management
- **ACID Compliance** - Critical for financial data integrity

## Documentation

- **[Database Schema](schema.html)** - Table structures, relationships, and JSONB formats
- **[Database Migrations](migrations.html)** - Alembic migration commands and workflows
- **[Database Queries](queries.html)** - Useful SQL queries for data inspection

## Related Documentation

- **[Backend Architecture](../backend/architecture.html)** - Connection pool management, repository pattern, and service layer

## Quick Reference

```bash
# Run migrations
cd backend
make migrate

# Create new migration
make migration MESSAGE="description"

# Rollback migration
make rollback
```
