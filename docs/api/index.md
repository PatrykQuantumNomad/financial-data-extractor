---
layout: default
title: API
description: REST API documentation, endpoints, request/response formats, and examples
nav_order: 6
has_children: true
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

## API Request Flow

The following diagram illustrates how a request flows through the API layers from client to database:

```mermaid
sequenceDiagram
    participant Client
    participant API as FastAPI API
    participant Service as Service Layer
    participant Repository as Repository Layer
    participant DB as PostgreSQL
    
    Client->>API: HTTP Request<br/>(JSON)
    API->>API: Request Validation<br/>(Pydantic Models)
    API->>API: Dependency Injection<br/>(get_service, get_repository)
    API->>Service: Call Service Method<br/>(Business Logic)
    Service->>Service: Business Logic<br/>(Validation, Transformation)
    Service->>Repository: Repository Method<br/>(Data Access)
    Repository->>Repository: Build SQL Query<br/>(SQLAlchemy Core)
    Repository->>DB: Execute Query<br/>(Connection Pool)
    DB-->>Repository: Query Result<br/>(Rows as Dicts)
    Repository-->>Service: Domain Object<br/>(Pydantic Model)
    Service-->>API: Service Response<br/>(Business Object)
    API->>API: Serialize Response<br/>(JSON)
    API-->>Client: HTTP Response<br/>(JSON)
    
    Note over API,DB: Connection Pool<br/>manages database<br/>connections efficiently
    Note over Service,Repository: Clear separation<br/>of business logic<br/>and data access
```

**Key Flow Points:**

1. **Request Validation**: FastAPI validates incoming JSON against Pydantic models
2. **Dependency Injection**: Services and repositories are injected via FastAPI's dependency system
3. **Service Layer**: Contains business logic and orchestrates repository calls
4. **Repository Layer**: Encapsulates all database operations using SQLAlchemy Core
5. **Connection Pool**: Manages database connections efficiently (created at startup)
6. **Response Serialization**: Domain objects are automatically serialized to JSON

## Complete API Reference

**[API Reference](reference.html)** - Complete documentation of all endpoints, request/response formats, examples, and error handling.

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
