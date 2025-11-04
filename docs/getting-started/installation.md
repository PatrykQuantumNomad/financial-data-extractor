---
layout: default
title: Installation
description: Detailed installation and setup instructions
nav_order: 2
parent: Getting Started
---

# Installation Guide

This guide covers the complete installation and setup process for the Financial Data Extractor.

## Prerequisites

### Required Software

- **Python 3.13** - Backend runtime
- **UV package manager** - Python dependency management (install from [github.com/astral-sh/uv](https://github.com/astral-sh/uv))
- **Node.js 18+** - Frontend runtime
- **Docker & Docker Compose** - Infrastructure services
- **Git** - Version control

### Required Services (via Docker)

- **PostgreSQL 16+** - Primary database
- **Redis 8+** - Cache and Celery broker
- **MinIO** - Object storage for PDFs

### External Services

- **OpenRouter API Key** - For LLM access (get from [OpenRouter.ai](https://openrouter.ai))

## Step-by-Step Installation

### 1. Clone the Repository

```bash
git clone https://github.com/PatrykQuantumNomad/financial-data-extractor.git
cd financial-data-extractor
```

### 2. Set Up Infrastructure

Start all required services using Docker Compose:

```bash
cd infrastructure
make up-dev
```

This starts:
- PostgreSQL (port 5432)
- Redis (port 6379)
- MinIO (API: 9000, Console: 9001)
- Monitoring stack (Prometheus, Grafana, Loki, Flower)

**Verify Services:**

```bash
# Check Docker containers
docker ps

# Check PostgreSQL
docker exec -it fde-postgres psql -U postgres -d financial_data_extractor -c "SELECT version();"

# Check Redis
docker exec -it fde-redis redis-cli ping

# Check MinIO (in browser)
# http://localhost:9001 (minioadmin/minioadmin)
```

### 3. Configure Environment Variables

Create `.env` files in the backend directory:

```bash
cd ../backend
cp .env.example .env
```

Edit `.env` and configure:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/financial_data_extractor

# Redis
REDIS_URL=redis://localhost:6379/0

# OpenRouter (required)
OPEN_ROUTER_API_KEY=your_openrouter_api_key_here
OPEN_ROUTER_MODEL_SCRAPING=openai/gpt-4o-mini
OPEN_ROUTER_MODEL_EXTRACTION=openai/gpt-4o-mini

# MinIO
MINIO_ENABLED=true
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=financial-documents
MINIO_USE_SSL=false
```

### 4. Set Up Backend

```bash
# Install dependencies
make install-dev

# Run database migrations
make migrate

# Verify installation
make test
```

### 5. Set Up Frontend

```bash
cd ../frontend

# Install dependencies
npm install

# Verify installation
npm run type-check
npm test
```

### 6. Start Services

**Terminal 1 - Backend API:**

```bash
cd backend
make run
```

**Terminal 2 - Celery Worker:**

```bash
cd backend
make celery-worker
```

**Terminal 3 - Frontend:**

```bash
cd frontend
npm run dev
```

## Verification

### Check Backend

```bash
# Health check
curl http://localhost:3030/healthcheck

# API docs
# Open http://localhost:3030/docs in browser
```

### Check Frontend

```bash
# Open http://localhost:3000 in browser
```

### Check Infrastructure

- **Grafana**: http://localhost:3200 (admin/admin)
- **Flower**: http://localhost:5555
- **MinIO Console**: http://localhost:9001 (minioadmin/minioadmin)
- **Prometheus**: http://localhost:9090

## Troubleshooting

### Common Issues

**Database Connection Errors:**
- Verify PostgreSQL is running: `docker ps | grep postgres`
- Check DATABASE_URL in `.env`
- Verify network connectivity: `docker exec -it fde-postgres psql -U postgres -c "SELECT 1;"`

**Redis Connection Errors:**
- Verify Redis is running: `docker ps | grep redis`
- Test connection: `docker exec -it fde-redis redis-cli ping`

**MinIO Connection Errors:**
- Verify MinIO is running: `docker ps | grep minio`
- Check MinIO console: http://localhost:9001
- Verify credentials in `.env`

**OpenRouter API Errors:**
- Verify API key is set in `.env`
- Check API key is valid: Test at https://openrouter.ai
- Verify you have credits/balance

**Port Conflicts:**
- Check if ports are already in use: `lsof -i :3030` (or other ports)
- Stop conflicting services or change ports in docker-compose

## Next Steps

After successful installation:

1. **[First Steps](first-steps.html)** - Run your first extraction
2. **[Architecture Overview](../architecture/)** - Understand the system design
3. **[API Reference](../api/reference.html)** - Explore the API

## Additional Resources

- **[Development Setup](../infrastructure/development.html)** - Detailed development environment guide
- **[Database Setup](../database/migrations.html)** - Database migration guide
- **[Infrastructure Overview](../infrastructure/)** - Complete infrastructure documentation
