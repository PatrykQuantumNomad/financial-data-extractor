---
layout: default
title: Infrastructure
description: Docker setup, development environment, and task processing
nav_order: 6
has_children: true
---

# Infrastructure Documentation

Infrastructure and operations documentation for the Financial Data Extractor platform, covering Docker setup, development environments, and task processing.

## Infrastructure Overview

The platform uses containerized services managed with Docker Compose:

- **FastAPI Backend** - REST API server
- **PostgreSQL** - Primary database
- **Redis** - Caching and Celery message broker
- **Celery Workers** - Background task processing
- **Flower** - Celery task monitoring

## Documentation

- **[Development Setup](development.md)** - Docker Compose setup, service management, and development workflows
- **[Task Processing](tasks.md)** - Celery task system, workers, Flower monitoring, and task management

## Quick Start

```bash
cd infrastructure/docker
docker-compose -f docker-compose.dev.yml up -d
```

## Related Documentation

- **[Backend Documentation](../backend/index.md)** - Backend architecture and setup
- **[Database Documentation](../database/index.md)** - Database schema and migrations
