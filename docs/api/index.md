---
layout: default
title: API
description: REST API documentation, endpoints, request/response formats, and examples
nav_order: 5
has_children: false
---

# API Documentation

The Financial Data Extractor provides a comprehensive REST API built with FastAPI for managing companies, documents, financial statement extractions, and compiled statements.

## API Overview

- **Base URL**: `http://localhost:3030/api/v1`
- **API Version**: v1 (URL-based versioning)
- **Format**: JSON
- **Error Format**: RFC 7807 Problem Details

## Interactive Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: `http://localhost:3030/docs`
- **ReDoc**: `http://localhost:3030/redoc`
- **OpenAPI Schema**: `http://localhost:3030/openapi.json`

## Complete API Reference

**[API Reference](reference.md)** - Complete documentation of all endpoints, request/response formats, examples, and error handling.

## API Resources

- **Companies** - Manage company information
- **Documents** - Manage PDF documents (annual reports, presentations)
- **Extractions** - Manage extracted financial statements
- **Compiled Statements** - Manage compiled multi-year financial statements
- **Tasks** - Trigger and monitor Celery tasks

## Authentication

Currently, the API operates without authentication in development. Production deployments should implement OAuth2 with JWT tokens.

## Rate Limiting

No rate limits are currently enforced. Production deployments should implement rate limiting to prevent abuse of expensive operations.

## Monitoring

The API exposes Prometheus metrics at `/metrics` for monitoring request latency, counts, error rates, and more.
