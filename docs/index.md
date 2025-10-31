---
layout: default
title: Financial Data Extractor
description: Automated platform to extract, normalize, and compile 10 years of financial statements from European company annual reports
nav_enabled: true
---

# Financial Data Extractor

An automated platform that scrapes, classifies, parses, and compiles multi-year financial statements (Income Statement, Balance Sheet, Cash Flow Statement) from European company investor relations websites.

## Project Overview

The Financial Data Extractor automates the labor-intensive process of collecting and standardizing financial data from annual reports. It handles:

- **Web Scraping**: Automated discovery and download of annual reports from investor relations websites
- **Document Classification**: Intelligent categorization of PDFs (Annual Reports, Presentations, etc.)
- **Data Extraction**: LLM-powered parsing of financial statements from PDF documents
- **Normalization**: Fuzzy matching and deduplication of line items across multiple years
- **Compilation**: Aggregation of 10 years of financial data into unified views

### Core Objectives

1. **Scrape & Classify**: Identify and categorize PDFs from investor relations websites
2. **Parse**: Extract financial data from Annual Reports using GPT-5/LLM
3. **Compile**: Aggregate 10 years of financial data into unified views
4. **Deduplicate**: Align and merge similarly-named line items across years
5. **Prioritize Latest**: Use restated data from newer reports when available

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
        B2[Business Logic]
        B --> B1
        B --> B2
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
        F[OpenAI GPT-5 API]
        G[File Storage - PDFs]
    end

    A -->|REST API| B
    B -->|Queue Tasks| C
    B -->|Store Data| D
    B -->|Cache & Broker| E
    W1 -->|Store PDFs| G
    W1 -->|Metadata| D
    W2 -->|Extract Data| F
    W2 -->|Raw Extractions| D
    W3 -->|Compiled Statements| D
    C -->|Task Queue| E
    W1 -->|Read Cache| E
    W2 -->|Read Cache| E

    classDef frontend fill:#e1f5ff,stroke:#01579b,stroke-width:2px
    classDef api fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef processing fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef data fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
    classDef external fill:#fce4ec,stroke:#880e4f,stroke-width:2px

    class A,A1,A2,A3 frontend
    class B,B1,B2 api
    class C,W1,W2,W3 processing
    class D,E data
    class F,G external
```

## Data Flow

### Phase 1: Scraping & Classification

1. User initiates extraction for a company via the frontend
2. FastAPI receives request and creates a job record
3. Task is enqueued to Celery
4. Worker scrapes the investor relations website
5. Identifies and downloads all PDFs (annual reports, presentations, etc.)
6. Classifies documents by type using filename patterns, metadata, and content sampling
7. Stores PDFs in file storage and creates database records with metadata

### Phase 2: Parsing & Extraction

1. For each Annual Report PDF:
2. Worker extracts text and tables using PyMuPDF/pdfplumber for structured tables
3. For scanned documents, OCR (Tesseract/AWS Textract) is used
4. Extracted content is sent to GPT-5 with structured prompts
5. GPT-5 returns structured financial data (Income Statement, Balance Sheet, Cash Flow)
6. Data is validated against schemas and business rules
7. Raw extraction is stored in database as JSON

### Phase 3: Normalization & Compilation

1. For each statement type across all years:
2. System collects all line items from all reports
3. Normalizes line item names using fuzzy matching and manual mappings
4. Detects and prioritizes restated data (newer reports override older values)
5. Builds unified table with 10 years of columns
6. Fills in data prioritizing latest sources
7. Stores compiled view in database with metadata (data lineage, confidence scores)

## Technology Stack

### Backend

- **FastAPI** - High-performance async web framework
- **Celery** - Distributed task queue for background processing
- **PostgreSQL** - Primary database with JSONB support
- **Redis** - Caching layer and Celery message broker
- **SQLAlchemy** - ORM for database operations
- **Alembic** - Database migrations

### Frontend

- **Next.js 15** - React framework with App Router
- **React** - UI library
- **TailwindCSS** - Utility-first CSS framework
- **shadcn/ui** - Component library

### Processing & AI

- **OpenAI GPT-5** - Financial statement extraction from PDFs
- **PyMuPDF** - PDF processing and table extraction
- **pdfplumber** - Alternative PDF text extraction
- **rapidfuzz** - Fuzzy string matching for line item normalization

## Documentation

This documentation site provides comprehensive guides for:

- **Backend Development** - FastAPI setup, database models, API endpoints
- **Frontend Development** - Next.js components, data visualization
- **PDF Processing** - Scraping, classification, and extraction workflows
- **Financial Normalization** - Line item matching and multi-year compilation
- **Infrastructure** - Docker, deployment, monitoring
- **Testing** - Unit, integration, and end-to-end testing strategies

## Quick Start

See the [Backend README](../backend/README.md) for setup instructions and development workflows.

## License

Financial Data Extractor is released under the MIT License. See the [LICENSE](https://github.com/PatrykQuantumNomad/financial-data-extractor/blob/main/LICENSE){:target="\_blank"} file for more details.
