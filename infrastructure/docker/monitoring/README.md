# Observability Stack Setup

This directory contains the configuration for the observability stack used in development:

- **Prometheus**: Metrics collection and storage
- **Grafana**: Metrics visualization and dashboards
- **Loki**: Log aggregation
- **Promtail**: Log collection agent

## Services

### Prometheus (Port 9090)

- Scrapes metrics from:
  - FastAPI application (localhost:3030/metrics)
  - PostgreSQL exporter (postgres-exporter:9187)
  - Redis exporter (redis-exporter:9121)
  - Celery workers (host.docker.internal:9091/metrics)
  - Flower (flower:5555/metrics)

### Grafana (Port 3200)

- Default credentials: `admin` / `admin`
- Pre-configured datasources:
  - Prometheus (http://prometheus:9090)
  - Loki (http://loki:3100)

### Loki (Port 3100)

- Log aggregation system
- Receives logs from Promtail

### Promtail

- Collects logs from Docker containers
- Sends logs to Loki

## Setup Instructions

1. **Start the observability stack:**

   ```bash
   cd infrastructure/docker
   docker-compose -f docker-compose.dev.yml up -d prometheus grafana loki promtail postgres-exporter redis-exporter
   ```

2. **Access Grafana:**

   - Open http://localhost:3200
   - Login with `admin` / `admin`
   - Dashboards should be automatically loaded from `/var/lib/grafana/dashboards`

3. **Access Prometheus:**

   - Open http://localhost:9090
   - Check targets under Status → Targets

4. **Verify FastAPI metrics:**

   - Ensure your FastAPI app is running and exposes `/metrics` endpoint
   - Prometheus should scrape from `host.docker.internal:3030/metrics`
   - If running FastAPI in Docker, update the target in `prometheus/prometheus.yml`

5. **Verify Celery metrics:**
   - Start a Celery worker: `celery -A app.tasks.celery_app worker --loglevel=info`
   - The worker will automatically start a Prometheus metrics server on port 9091
   - Prometheus will scrape from `host.docker.internal:9091/metrics`

## Dashboard Notes

The dashboards in `grafana/dashboards/` are simplified templates. You may need to:

1. **Import or create dashboards in Grafana UI:**

   - Go to Dashboards → Import
   - Create dashboards based on available metrics
   - Or use the provided templates as a starting point

2. **Adjust metric names:**

   - FastAPI metrics use prefix `http_` from starlette-exporter
   - Celery metrics use prefix `celery_` from our custom metrics module
   - PostgreSQL metrics use prefix `pg_` from postgres-exporter
   - Redis metrics use prefix `redis_` from redis-exporter

3. **Common metric queries:**

   **FastAPI:**

   ```promql
   rate(http_requests_total{app="financial-data-extractor-api"}[5m])
   histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
   ```

   **Celery:**

   ```promql
   rate(celery_tasks_total[5m])
   histogram_quantile(0.95, rate(celery_task_duration_seconds_bucket[5m]))
   ```

   **PostgreSQL:**

   ```promql
   rate(pg_stat_database_xact_commit[5m])
   pg_stat_database_numbackends
   ```

   **Redis:**

   ```promql
   rate(redis_commands_processed_total[5m])
   redis_memory_used_bytes
   ```

## Troubleshooting

### Prometheus can't scrape FastAPI

- Ensure FastAPI is running and `/metrics` endpoint is accessible
- Check if running in Docker - update target to service name instead of `host.docker.internal`
- Verify network connectivity from Prometheus container

### Prometheus can't scrape Celery workers

- Ensure Celery worker is running and metrics module is imported
- Check that port 9091 is not blocked
- Verify `host.docker.internal` works on your platform (Docker Desktop) or use actual IP

### Grafana dashboards not loading

- Check datasource connections in Grafana Settings → Data Sources
- Verify Prometheus and Loki are accessible from Grafana container
- Dashboards may need to be manually imported or created

### Logs not appearing in Loki

- Check Promtail is running and connected to Docker socket
- Verify Promtail config has correct Loki URL
- Check Promtail logs: `docker logs fde-promtail`

## Network Configuration

All services are on the `fde-dev-network` bridge network. If running services outside Docker:

- Use `host.docker.internal` (Docker Desktop) to access host services
- Or add services to the same Docker network
- Or configure proper host networking
