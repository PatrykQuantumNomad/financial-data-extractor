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

### 2. Configure Environment Variables

**⚠️ IMPORTANT: Configure environment variables BEFORE starting any servers.**

Both backend and frontend require `.env` files to be set up from their respective `.env.example` templates.

#### Backend Environment Variables

Create `.env` file in the backend directory:

```bash
cd backend
cp .env.example .env
```

Edit `backend/.env` and configure the required values:

```bash
# OpenRouter API Key (REQUIRED - get from https://openrouter.ai)
OPEN_ROUTER_API_KEY=your_openrouter_api_key_here

# OpenRouter models
OPEN_ROUTER_MODEL_SCRAPING=openai/gpt-4.1-mini
OPEN_ROUTER_MODEL_EXTRACTION=openai/gpt-4.1-mini

# Database configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=financial_data_extractor
DB_USERNAME=postgres
DB_PASSWORD=postgres

# Redis configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# MinIO configuration
MINIO_ENABLED=true
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=financial-documents
MINIO_USE_SSL=false
```

**Critical Configuration:**
- `OPEN_ROUTER_API_KEY` - **Required** for LLM operations. Get your API key from [OpenRouter.ai](https://openrouter.ai)
- Database and Redis settings should match your Docker Compose configuration
- MinIO settings use default credentials for development

#### Frontend Environment Variables

Create `.env` file in the frontend directory:

```bash
cd frontend
cp .env.example .env
```

Edit `frontend/.env` and configure if needed:

```bash
# App Configuration
NEXT_PUBLIC_APP_URL="http://localhost:3000"
NEXT_PUBLIC_API_URL="http://localhost:3030"
NEXT_PUBLIC_APP_NAME="Financial Data Extractor"
NODE_ENV="development"
NEXT_PUBLIC_LOG_LEVEL="debug"
```

**Note:** Default values work for local development. Adjust `NEXT_PUBLIC_API_URL` if your backend runs on a different port.

### 3. Set Up Infrastructure

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

### 4. Set Up Backend

**Note:** Ensure you've completed Step 2 (Environment Variables) before proceeding.

```bash
# Install dependencies
make install-dev

# Run database migrations
make migrate

# Verify installation
make test
```

### 5. Set Up Frontend

**Note:** Ensure you've completed Step 2 (Environment Variables) before proceeding.

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
