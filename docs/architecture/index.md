---
layout: default
title: Architecture Overview
description: System architecture, data flow, and technology decisions
nav_order: 3
has_children: true
---

# Architecture Overview

The Financial Data Extractor is built with a modern, scalable architecture that separates concerns and enables independent scaling of components.

## System Architecture

```mermaid
graph TB
    subgraph "Frontend Layer"
        A[Next.js Application]
        A1[Dashboard - 10yr View]
        A2[Financial Tables]
        A3[Extraction Form]
        A --> A1
        A --> A2
        A --> A3
    end

    subgraph "API Layer"
        B[FastAPI Backend]
        B1[REST API Endpoints]
        B2[API Exception Handler]
        B3[Problem Details RFC 7807]
        B --> B1
        B1 --> B2
        B2 --> B3
    end

    subgraph "Service Layer"
        S1[Business Logic Services]
        S2[Service Exceptions]
        S3[Exception Translators]
        S1 --> S2
        S2 --> S3
        S3 --> B2
    end

    subgraph "Repository Layer"
        R1[Database Repositories]
        R2[DB Exceptions]
        R1 --> R2
        R2 --> S3
    end

    subgraph "Processing Layer"
        C[Celery Task Queue]
        W1[Worker 1: Scrape & Classify]
        W2[Worker 2: Parse & Extract]
        W3[Worker 3: Normalize & Compile]
        C --> W1
        C --> W2
        C --> W3
    end

    subgraph "Data Layer"
        D[PostgreSQL Database]
        E[Redis Cache & Broker]
    end

    subgraph "External Services"
        F[OpenRouter LLM API]
        G[MinIO Object Storage]
    end

    A -->|REST API| B1
    B1 --> S1
    S1 --> R1
    R1 --> D
    B -->|Queue Tasks| C
    B -->|Store Data| D
    B -->|Cache & Broker| E
    W1 -->|Store PDFs| G
    W1 -->|Metadata| D
    W2 -->|Extract Data| F
    W2 -->|Read PDFs| G
    W2 -->|Raw Extractions| D
    W3 -->|Compiled Statements| D
    C -->|Task Queue| E
    W1 -->|Read Cache| E
    W2 -->|Read Cache| E

    classDef frontend fill:#e1f5ff,stroke:#01579b,stroke-width:2px
    classDef api fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef service fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef repository fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef processing fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef data fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
    classDef external fill:#fce4ec,stroke:#880e4f,stroke-width:2px

    class A,A1,A2,A3 frontend
    class B,B1,B2,B3 api
    class S1,S2,S3 service
    class R1,R2 repository
    class C,W1,W2,W3 processing
    class D,E data
    class F,G external
```

## Architecture Layers

### Frontend Layer
- **Next.js 15** with App Router
- Server Components for initial rendering
- Client Components with React Query for data fetching
- shadcn/ui component library

### API Layer
- **FastAPI** REST API
- Automatic OpenAPI documentation
- RFC 7807 Problem Details for errors
- Request/response validation

### Service Layer
- Business logic separation
- Service exception handling
- Exception translation to API errors

### Repository Layer
- Database abstraction
- SQLAlchemy async operations
- Repository pattern implementation

### Processing Layer
- **Celery** distributed task queue
- Three worker types for different tasks
- Task chaining and workflows

### Data Layer
- **PostgreSQL 16** for structured data
- **Redis** for caching and message broker
- **MinIO** for object storage

## Documentation

- **[Data Flow](data-flow.html)** - Detailed workflow from scraping to compilation
- **[Technology Decisions](technology-decisions.html)** - Why we chose each technology

## Related Documentation

- **[Backend Architecture](../backend/architecture.html)** - Backend implementation details
- **[Frontend Architecture](../frontend/architecture.html)** - Frontend implementation details
- **[Database Schema](../database/schema.html)** - Database structure
- **[Task Processing](../infrastructure/tasks.html)** - Celery task system
