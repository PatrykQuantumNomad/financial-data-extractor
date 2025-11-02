---
layout: default
title: Backend
description: FastAPI backend architecture, database, services, and testing
nav_order: 2
has_children: true
---

# Backend Documentation

The Financial Data Extractor backend is built with **FastAPI**, providing a high-performance, async API for managing companies, documents, financial statement extractions, and compiled statements.

## Architecture Overview

The backend uses a **layered architecture** with clear separation of concerns:

1. **API Layer** - REST API endpoints with automatic exception handling
2. **Service Layer** - Business logic with service exceptions
3. **Repository Layer** - Database operations with repository pattern
4. **Database Layer** - PostgreSQL with connection pooling

## Key Features

- **Layered Exception Handling**: Database → Service → API exception translation
- **Repository Pattern**: Clean separation of database operations
- **Dependency Injection**: FastAPI's dependency system for services and repositories
- **Connection Pooling**: Async connection pool management
- **Comprehensive Testing**: Unit tests (124) and integration tests (4) with testcontainers

## Documentation

### Architecture

- **[Database Architecture](database.md)** - Connection pool management, dependency injection, repository pattern, and exception handling
- **[Testing Guide](testing.md)** - pytest setup, unit tests, integration tests with testcontainers

### Related Documentation

- **[Database Schema](../database/schema.md)** - Table structures and relationships
- **[Database Migrations](../database/migrations.md)** - Alembic migration workflows
- **[API Reference](../api/reference.md)** - Complete REST API documentation

## Technology Stack

- **FastAPI** - High-performance async web framework
- **PostgreSQL** - Primary database with JSONB support
- **SQLAlchemy** - ORM for database models
- **Alembic** - Database migrations
- **pytest** - Testing framework
- **testcontainers** - Integration testing with real databases

## Quick Start

```bash
cd backend
make install-dev
make migrate
make run
```

See the [Backend README](../../backend/README.md) for detailed setup instructions.
