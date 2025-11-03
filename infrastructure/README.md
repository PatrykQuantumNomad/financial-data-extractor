# Infrastructure

## Local Dev

For local dev we deploy resources to support the application.

### Stack

- **PostgreSQL 16**: primary database (port 5432)
- **pgAdmin 4**: DB admin UI (port 5050)
- **Redis 8**: cache, Celery broker/result backend (port 6379)
- **Redis Commander**: Redis UI (port 8081)
- **MinIO**: S3-compatible object storage (API: port 9000, Console: port 9001)
- **Flower**: Celery task monitoring dashboard (port 5555)
- **Prometheus**: Metrics collection (port 9090)
- **Grafana**: Metrics visualization (port 3200)
- **Loki**: Log aggregation (port 3100)
- **Promtail**: Log shipper
- **PostgreSQL Exporter**: Database metrics (port 9187)
- **Redis Exporter**: Redis metrics (port 9121)

Compose file (dev): `docker/docker-compose.dev.yml`

### Prerequisites

- Docker Desktop (or Docker Engine + Docker Compose v2)

### Quick Start

From the repository root, use the infrastructure Makefile:

```bash
make up
```

This will start all services in the background and print URLs.

### Service URLs and Credentials (Dev)

- **Postgres**: `postgres://postgres:postgres@localhost:5432/financial_data_extractor`
- **pgAdmin**: `http://localhost:5050` (email: `admin@local.dev`, password: `adminadmin`)
- **Redis**: `redis://localhost:6379`
- **Redis Commander**: `http://localhost:8081`
- **MinIO API**: `http://localhost:9000`
- **MinIO Console**: `http://localhost:9001` (username: `minioadmin`, password: `minioadmin`)
- **Flower**: `http://localhost:5555` (Celery monitoring dashboard)
- **Prometheus**: `http://localhost:9090`
- **Grafana**: `http://localhost:3200` (username: `admin`, password: `admin`)
- **Loki**: `http://localhost:3100`

In pgAdmin, add a connection to host `postgres` (the service name), user `postgres`, password `postgres`, database `financial_data_extractor`.

### Makefile Commands (Dev)

All commands are executed from repo root with `-C infrastructure`:

```bash
# Start / stop
make up-dev      # start services (detached)
make down-dev    # stop and remove containers (keep volumes)
make destroy-dev # stop and remove containers + volumes
make reset-dev   # destroy then start fresh
make restart-dev # restart all services

# Inspect
make ps-dev      # show status
make logs-dev    # tail all logs
make logs-postgres-dev
make logs-redis-dev
make health      # quick health/status (dev)

# Tools / helpers
make psql        # open psql to Postgres
make redis-cli   # open redis-cli
make pgadmin     # open pgAdmin in browser
make url         # print service URLs (dev)
```
