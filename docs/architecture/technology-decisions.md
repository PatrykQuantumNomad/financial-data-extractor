---
layout: default
title: Technology Decisions
description: Rationale behind technology choices
nav_order: 3
parent: Architecture Overview
---

# Technology Decisions

This document explains the rationale behind key technology choices in the Financial Data Extractor.

## Why LLM for Extraction?

The platform uses **OpenRouter** as an API gateway to access multiple LLM providers (OpenAI, Anthropic, etc.), allowing flexible model selection:

1. **Flexibility**: Handles various report formats without custom parsers
2. **Accuracy**: State-of-the-art text understanding from multiple providers
3. **Hierarchy**: Understands nested line items and relationships
4. **Multi-language**: Can handle European languages
5. **Model Selection**: Choose optimal models per task (e.g., GPT-4o-mini for scraping, GPT-4o for extraction)

### Configuration

- **Scraping Model**: `openai/gpt-4o-mini` (fast, cost-effective for URL discovery)
- **Extraction Model**: `openai/gpt-4o-mini` (configurable, can use GPT-4o or Claude 3.5 Sonnet for better accuracy)
- **API Gateway**: OpenRouter provides unified interface to multiple providers

### Alternatives Considered

- **Traditional OCR + Rule-based parsing**: Too brittle, requires custom parsers for each format
- **LayoutLM/DocAI**: Requires training data and model training
- **AWS Textract**: Good but less flexible than modern LLMs
- **Direct OpenAI API**: OpenRouter provides better flexibility and cost management

### Why OpenRouter?

- **Multi-Provider**: Access to OpenAI, Anthropic, Google, and more
- **Cost Optimization**: Choose cost-effective models per task
- **Unified API**: Single interface for all providers
- **Model Selection**: Easy switching between models
- **Analytics**: Built-in usage tracking and cost monitoring

## Why PostgreSQL?

1. **JSONB**: Perfect for storing raw extractions and metadata
2. **Relational**: Strong for company/document relationships
3. **Mature**: Excellent tooling and performance
4. **ACID**: Critical for financial data integrity
5. **Async Support**: Excellent async driver (asyncpg) for FastAPI

### JSONB Benefits

- Store flexible financial data structures
- Efficient querying with GIN indexes
- No schema changes needed for new statement formats
- Maintains relational benefits for structured data

### Alternatives Considered

- **MongoDB**: Good for JSON, but weaker relational capabilities
- **MySQL**: Good relational, but weaker JSON support
- **SQLite**: Good for development, but not suitable for production scale

## Why Celery?

1. **Async Processing**: PDFs take minutes to process, LLM calls can take 2-5 minutes per document
2. **Retries**: Handle API failures, rate limits gracefully with exponential backoff
3. **Monitoring**: Flower dashboard for real-time task tracking and history
4. **Workflows**: Complex pipelines (scrape → classify → extract → compile) with task chaining
5. **Queue Management**: Dedicated queues for different task types (scraping, extraction, compilation, orchestration)
6. **Scalability**: Horizontal scaling with multiple workers across queues

### Task Types

- **Scraping Queue**: Web scraping tasks
- **Extraction Queue**: PDF processing and LLM extraction
- **Compilation Queue**: Normalization and compilation
- **Orchestration Queue**: High-level workflow coordination

### Alternatives Considered

- **RQ (Redis Queue)**: Simpler but less feature-rich
- **Dramatiq**: Good but less mature ecosystem
- **AWS SQS + Lambda**: Good for cloud, but vendor lock-in
- **Direct async functions**: Doesn't handle long-running tasks well

## Why FastAPI?

1. **Performance**: One of the fastest Python frameworks
2. **Async Support**: Native async/await support
3. **Auto Documentation**: Automatic OpenAPI/Swagger generation
4. **Type Safety**: Pydantic models for validation
5. **Modern Python**: Uses latest Python features (type hints, async)

### Key Features Used

- **Dependency Injection**: Clean service layer architecture
- **Background Tasks**: For lightweight async operations
- **WebSockets**: For real-time updates (future)
- **Middleware**: CORS, request ID, timeout handling

### Alternatives Considered

- **Flask**: Good but slower, less async support
- **Django**: Too heavy, synchronous by default
- **Tornado**: Good async but less modern
- **Starlette**: FastAPI is built on Starlette, but FastAPI adds more features

## Why Next.js 15?

1. **App Router**: Modern routing with Server Components
2. **Server Components**: Better performance and SEO
3. **React 19**: Latest React features
4. **TypeScript**: Full type safety
5. **Built-in Optimizations**: Image optimization, code splitting, etc.

### Key Features Used

- **Server Components**: Initial rendering on server
- **Client Components**: Interactivity with React Query
- **API Routes**: Backend integration (if needed)
- **Static Generation**: For documentation pages

### Alternatives Considered

- **Create React App**: Deprecated, no SSR
- **Vite + React**: Good but requires manual SSR setup
- **Remix**: Good but less mature ecosystem
- **SvelteKit**: Good but smaller ecosystem

## Why React Query?

1. **Caching**: Automatic request caching and deduplication
2. **Background Updates**: Automatic data synchronization
3. **Optimistic Updates**: Better UX for mutations
4. **DevTools**: Excellent debugging tools
5. **Error Handling**: Built-in error states and retries

### Benefits

- **Automatic Caching**: No manual cache management
- **Request Deduplication**: Multiple components share same request
- **Background Refetching**: Keep data fresh automatically
- **Optimistic Updates**: Update UI before server confirms

### Alternatives Considered

- **SWR**: Good but less feature-rich
- **Apollo Client**: Good but GraphQL-focused
- **Redux + RTK Query**: Good but more complex
- **Manual fetch**: Too much boilerplate

## Why MinIO?

1. **S3-Compatible**: Easy migration to AWS S3
2. **Local Development**: Run locally with Docker
3. **Scalability**: Handles large files well
4. **Cost-Effective**: Free for development, cheaper than S3 for production
5. **API Compatibility**: Works with any S3 client

### Use Cases

- **PDF Storage**: Store all scraped PDFs
- **Backup**: Easy backup to S3
- **Development**: Local development without cloud costs

### Alternatives Considered

- **Local File System**: Simple but doesn't scale
- **AWS S3**: Good but vendor lock-in, costs
- **Google Cloud Storage**: Good but vendor lock-in
- **Azure Blob Storage**: Good but vendor lock-in

## Why Redis?

1. **Caching**: Fast in-memory caching
2. **Celery Broker**: Message broker for task queue
3. **Performance**: Sub-millisecond latency
4. **Persistence**: Optional persistence for durability
5. **Data Structures**: Rich data types (sets, lists, etc.)

### Use Cases

- **API Response Caching**: Cache expensive API calls
- **Session Storage**: User sessions (future)
- **Rate Limiting**: Track API usage (future)
- **Task Queue**: Celery message broker

### Alternatives Considered

- **Memcached**: Good caching but no broker functionality
- **RabbitMQ**: Good broker but heavier, not needed for caching
- **PostgreSQL**: Can be used as broker but slower

## Monitoring Stack

### Why Prometheus + Grafana?

- **Prometheus**: Industry standard for metrics
- **Grafana**: Best visualization tool
- **Integration**: Easy integration with FastAPI, PostgreSQL, Redis
- **Alerts**: Built-in alerting capabilities

### Why Loki?

- **Log Aggregation**: Centralized log storage
- **Grafana Integration**: View logs in Grafana
- **Label-based Queries**: Efficient log queries
- **Cost-Effective**: Cheaper than cloud log services

### Why Flower?

- **Celery-Specific**: Built for Celery monitoring
- **Real-time**: Live task monitoring
- **Task History**: Persistent task history
- **Easy Setup**: Simple Docker setup

## Related Documentation

- **[Data Flow](data-flow.html)** - How data moves through the system
- **[Backend Architecture](../backend/architecture.html)** - Backend implementation
- **[Infrastructure Setup](../infrastructure/development.html)** - Service configuration
