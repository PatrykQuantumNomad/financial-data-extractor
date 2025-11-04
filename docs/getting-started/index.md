---
layout: default
title: Getting Started
description: Quick start guide for setting up and using the Financial Data Extractor
nav_order: 2
has_children: true
---

# Getting Started

Welcome to the Financial Data Extractor! This guide will help you get up and running quickly.

## Quick Start

The fastest way to get started:

```bash
# Clone the repository
git clone https://github.com/PatrykQuantumNomad/financial-data-extractor.git
cd financial-data-extractor

# Start infrastructure services (PostgreSQL, Redis, MinIO, monitoring)
cd infrastructure
make up-dev

# Setup backend
cd ../backend
make install-dev
make migrate

# Start backend server (in one terminal)
make run

# Start Celery worker (in another terminal)
make celery-worker

# Setup frontend (in a third terminal)
cd ../frontend
npm install
npm run dev
```

**Access Points:**

- **Frontend**: `http://localhost:3000`
- **Backend API**: `http://localhost:3030`
- **API Docs**: `http://localhost:3030/docs`
- **Grafana**: `http://localhost:3200` (admin/admin)
- **Flower**: `http://localhost:5555`
- **MinIO Console**: `http://localhost:9001` (minioadmin/minioadmin)

## Next Steps

1. **[Installation Guide](installation.html)** - Detailed setup instructions and prerequisites
2. **[First Extraction](first-steps.html)** - Tutorial for your first financial data extraction

## Documentation

For detailed information, see:

- **[Architecture Overview](../architecture/)** - System design and architecture
- **[Backend Documentation](../backend/)** - Backend setup and development
- **[Frontend Documentation](../frontend/)** - Frontend setup and development
- **[API Reference](../api/)** - Complete API documentation
- **[Infrastructure Setup](../infrastructure/)** - Docker and service configuration
