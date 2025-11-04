---
layout: default
title: Infrastructure Development Setup
description: Docker Compose setup, infrastructure services, and development environment configuration
nav_order: 2
parent: Infrastructure
---

# Infrastructure Development Setup

This guide covers setting up the development infrastructure using Docker Compose, including PostgreSQL, Redis, pgAdmin, and Redis Commander.

## Quick Start

```bash
# Start all infrastructure services
cd infrastructure
make up-dev

# Check service status
make health
make ps

# View service URLs and connection strings
make url

# Apply database migrations
cd ../backend
make migrate
```

## Infrastructure Services

The development environment includes the following services:

- **PostgreSQL** - Primary database (port 5432)
- **pgAdmin** - Database administration UI (port 5050)
- **Redis** - Caching and Celery message broker (port 6379)
- **Redis Commander** - Redis administration UI (port 8081)
- **MinIO** - S3-compatible object storage for PDF files (API: port 9000, Console: port 9001)
- **Flower** - Celery task monitoring dashboard (port 5555)
- **Prometheus** - Metrics collection and storage (port 9090)
- **Grafana** - Metrics visualization and dashboards (port 3200)
- **Loki** - Log aggregation (port 3100)
- **Promtail** - Log shipper for Loki
- **PostgreSQL Exporter** - Prometheus exporter for PostgreSQL metrics (port 9187)
- **Redis Exporter** - Prometheus exporter for Redis metrics (port 9121)

## Infrastructure Makefile Commands

All infrastructure operations are managed through the Makefile in the `infrastructure/` directory:

```bash
cd infrastructure

# Service Management
make up-dev          # Start all services (PostgreSQL, Redis, pgAdmin, Redis Commander)
make down-dev        # Stop services (keep volumes)
make destroy-dev     # Stop and remove volumes (WARNING: destroys data)
make restart-dev     # Restart all services
make ps-dev          # Show service status

# Monitoring & Debugging
make health          # Check container health
make url             # Print service URLs and connection strings
make logs-dev        # View all service logs
make logs-postgres-dev  # View PostgreSQL logs
make logs-redis-dev     # View Redis logs

# Database Access
make psql            # Connect to PostgreSQL via psql
make pgadmin         # Open pgAdmin in browser
make redis-cli       # Connect to Redis CLI
```

### Shortcuts

The following shortcuts default to DEV stack:

```bash
make up              # Alias for make up-dev
make down            # Alias for make down-dev
make destroy         # Alias for make destroy-dev
make restart         # Alias for make restart-dev
make ps              # Alias for make ps-dev
make logs            # Alias for make logs-dev
make logs-postgres   # Alias for make logs-postgres-dev
make logs-redis      # Alias for make logs-redis-dev
```

## Service Configuration

### PostgreSQL

**Connection Details:**

- **Host**: `localhost` (or `postgres` if connecting from another Docker container)
- **Port**: `5432`
- **Database**: `financial_data_extractor`
- **Username**: `postgres`
- **Password**: `postgres`
- **Connection String**: `postgresql://postgres:postgres@localhost:5432/financial_data_extractor`

**Service Configuration:**

```yaml
postgres:
  image: postgres:16-alpine
  container_name: fde-postgres
  environment:
    POSTGRES_DB: financial_data_extractor
    POSTGRES_USER: postgres
    POSTGRES_PASSWORD: postgres
  ports:
    - "5432:5432"
  volumes:
    - postgres-data:/var/lib/postgresql/data
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U $$POSTGRES_USER -d $$POSTGRES_DB"]
    interval: 5s
    timeout: 5s
    retries: 10
```

### pgAdmin

**Access Details:**

- **URL**: <http://localhost:5050>
- **Email**: `admin@local.dev`
- **Password**: `adminadmin`

**Setup Instructions:**

1. Open pgAdmin: `make pgadmin` or navigate to <http://localhost:5050>
2. Login with credentials above
3. Right-click "Servers" → "Create" → "Server"
4. **General Tab**: Name: `Financial Data Extractor`
5. **Connection Tab**:
   - Host: `postgres` (or `localhost` if connecting from host)
   - Port: `5432`
   - Database: `financial_data_extractor`
   - Username: `postgres`
   - Password: `postgres`
6. Click "Save"

### Redis

**Connection Details:**

- **Host**: `localhost`
- **Port**: `6379`
- **Connection String**: `redis://localhost:6379`

### Redis Commander

**Access Details:**

- **URL**: <http://localhost:8081>

### MinIO

**Access Details:**

- **S3 API**: `http://localhost:9000`
- **Web Console**: `http://localhost:9001`
- **Username**: `minioadmin`
- **Password**: `minioadmin`
- **Default Bucket**: `financial-documents` (auto-created on first use)

**Usage:**

MinIO is used for storing PDF documents instead of local file system. The storage service automatically creates the bucket if it doesn't exist.

### Flower

**Access Details:**

- **URL**: `http://localhost:5555`
- **Persistent Mode**: Enabled (task history stored in SQLite)

Flower provides real-time monitoring of Celery tasks, workers, and queues. See [Task Processing Documentation](tasks.html) for details.

### Prometheus

**Access Details:**

- **URL**: `http://localhost:9090`
- **Metrics Endpoint**: `http://localhost:3030/metrics` (from FastAPI backend)

Prometheus scrapes metrics from:
- FastAPI backend (`/metrics` endpoint)
- PostgreSQL exporter (port 9187)
- Redis exporter (port 9121)

### Grafana

**Access Details:**

- **URL**: `http://localhost:3200`
- **Username**: `admin`
- **Password**: `admin`

Grafana is pre-configured with:
- Prometheus data source
- Loki data source (for logs)
- Pre-built dashboards for API metrics, database metrics, and Redis metrics

**First Login:**

1. Navigate to `http://localhost:3200`
2. Login with `admin` / `admin`
3. Change password when prompted (optional, can skip)

### Loki

**Access Details:**

- **URL**: `http://localhost:3100`
- **Query API**: `http://localhost:3100/loki/api/v1/query`

Loki aggregates logs from all services. Logs are queried via Grafana's Explore view.

## Environment Configuration

### Backend Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
# backend/.env (for Docker Compose)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=financial_data_extractor
DB_USERNAME=postgres
DB_PASSWORD=postgres

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=postgres  # Set if Redis requires password
REDIS_MAX_CONNECTIONS=10

# Or use DATABASE_URL directly
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/financial_data_extractor
```

### Connecting from Docker Container

If connecting from another Docker container (e.g., backend service), use the service name as host:

```bash
# Use service name as host
DB_HOST=postgres
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/financial_data_extractor

REDIS_HOST=redis
REDIS_PORT=6379
```

### Environment Variable Priority

The `alembic/env.py` file reads from environment variables with the following priority:

1. `DATABASE_URL` environment variable (highest priority)
2. Settings from `config.py` (reads from `.env` file using individual fields)
3. Default in `alembic.ini` (fallback)

## Service URLs

View all service URLs and connection strings:

```bash
cd infrastructure
make url
```

**Output:**

```
[DEV] Postgres:        postgres://postgres:postgres@localhost:5432/financial_data_extractor
[DEV] pgAdmin:         http://localhost:5050 (admin@local.dev / adminadmin)
[DEV] Redis:           redis://localhost:6379
[DEV] Redis Commander: http://localhost:8081
[DEV] MinIO API:       http://localhost:9000
[DEV] MinIO Console:   http://localhost:9001 (minioadmin / minioadmin)
[DEV] Flower:          http://localhost:5555
[DEV] Prometheus:      http://localhost:9090
[DEV] Grafana:         http://localhost:3200 (admin / admin)
[DEV] Loki:            http://localhost:3100
```

## Troubleshooting

### Database Container Not Running

```bash
# Check if containers are running
cd infrastructure
make ps-dev

# Start database if stopped
make up-dev

# Check database logs
make logs-postgres-dev
```

### Connection Refused

```bash
# Ensure database is healthy
cd infrastructure
make health

# Check database logs if unhealthy
make logs-postgres-dev

# Test connection directly
make psql

# Or view service URLs
make url
```

### Reset Infrastructure

**⚠️ WARNING: This will destroy all data!**

```bash
# Stop and remove containers with volumes
cd infrastructure
make destroy-dev

# Restart services
make up-dev

# Apply migrations
cd ../backend
make migrate
```

### Check Container Health

```bash
cd infrastructure
make health
make ps-dev
```

Services should show as "healthy" or "running" status.

## Docker Compose Files

The infrastructure configuration is defined in:

- **Development**: `infrastructure/docker/docker-compose.dev.yml`
- **Production**: `infrastructure/docker/docker-compose.prod.yml` (future)

All services use named volumes for data persistence:

- `postgres-data` - PostgreSQL data directory
- `pgadmin-data` - pgAdmin configuration
- `redis-data` - Redis persistence data
- `minio-data` - MinIO object storage data
- `flower-data` - Flower persistent task history
- `prometheus-data` - Prometheus metrics storage
- `grafana-data` - Grafana dashboards and configuration
- `loki-data` - Loki log storage

## Data Persistence

### Viewing Volumes

```bash
# List Docker volumes
docker volume ls | grep financial-data-extractor

# Inspect a volume
docker volume inspect financial-data-extractor-dev_postgres-data
```

### Backup PostgreSQL Data

```bash
# Create a backup
docker exec fde-postgres pg_dump -U postgres financial_data_extractor > backup.sql

# Restore from backup
docker exec -i fde-postgres psql -U postgres financial_data_extractor < backup.sql
```

## Next Steps

After setting up infrastructure:

1. **[Apply Database Migrations](../database/migrations.html)** - Set up the database schema
2. **[View Database Schema](../database/schema.html)** - Understand table structures
3. **[Run Useful Queries](../database/queries.html)** - Query and inspect data
