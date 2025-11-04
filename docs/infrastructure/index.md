---
layout: default
title: Infrastructure
description: Docker setup, development environment, and task processing
nav_order: 8
has_children: true
---

# Infrastructure Documentation

Infrastructure and operations documentation for the Financial Data Extractor platform, covering Docker setup, development environments, and task processing.

## Infrastructure Overview

The platform uses containerized services managed with Docker Compose:

### Core Services

- **PostgreSQL** - Primary database (port 5432)
- **Redis** - Caching and Celery message broker (port 6379)
- **MinIO** - S3-compatible object storage for PDFs (API: 9000, Console: 9001)

### Task Processing

- **Celery Workers** - Background task processing (runs locally or in containers)
- **Flower** - Celery task monitoring dashboard (port 5555)

### Monitoring & Observability

- **Prometheus** - Metrics collection and storage (port 9090)
- **Grafana** - Metrics visualization and dashboards (port 3200)
- **Loki** - Log aggregation (port 3100)
- **Promtail** - Log shipper for container logs
- **PostgreSQL Exporter** - Database metrics (port 9187)
- **Redis Exporter** - Cache and broker metrics (port 9121)

### Development Tools

- **pgAdmin** - Database administration UI (port 5050)
- **Redis Commander** - Redis administration UI (port 8081)

## Documentation

- **[Development Setup](development.html)** - Docker Compose setup, service management, and development workflows
- **[Task Processing](tasks.html)** - Celery task system, workers, Flower monitoring, and task management
- **[Object Storage](storage.html)** - MinIO object storage setup and usage

## Quick Start

```bash
# From repository root
cd infrastructure
make up-dev

# Or directly with docker-compose
cd infrastructure/docker
docker-compose -f docker-compose.dev.yml up -d
```

**Service URLs:**

- **PostgreSQL**: `postgres://postgres:postgres@localhost:5432/financial_data_extractor`
- **pgAdmin**: `http://localhost:5050` (admin@local.dev / adminadmin)
- **Redis**: `redis://localhost:6379`
- **MinIO Console**: `http://localhost:9001` (minioadmin / minioadmin)
- **Flower**: `http://localhost:5555`
- **Grafana**: `http://localhost:3200` (admin / admin)
- **Prometheus**: `http://localhost:9090`

## Related Documentation

- **[Backend Documentation](../backend/index.html)** - Backend architecture and setup
- **[Database Documentation](../database/index.html)** - Database schema and migrations
