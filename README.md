# Financial Data Extractor

An automated platform to scrape, classify, parse, and compile multi-year financial statements from European company investor relations websites.

## Project Overview

The Financial Data Extractor automates the labor-intensive process of collecting and standardizing financial data from annual reports. It handles:

- **Web Scraping**: Automated discovery and download of annual reports using intelligent LLM-powered extraction
- **Document Classification**: Categorization of PDFs (Annual Reports, Presentations, etc.)
- **Data Extraction**: LLM-powered parsing of financial statements from PDF documents
- **Normalization**: Fuzzy matching and deduplication of line items across multiple years
- **Compilation**: Aggregation of 10 years of financial data into unified views

### Core Objectives

1. **Scrape & Classify**: Identify and categorize PDFs from investor relations websites using Crawl4AI
2. **Parse**: Extract financial data from Annual Reports using LLM (via OpenRouter)
3. **Compile**: Aggregate 10 years of financial data into unified views
4. **Deduplicate**: Align and merge similarly-named line items across years
5. **Prioritize Latest**: Use restated data from newer reports when available

### Technology Stack

**Backend**: FastAPI, Celery, PostgreSQL, Redis, SQLAlchemy, Alembic  
**Frontend**: Next.js 15, React 19, TypeScript, TailwindCSS, shadcn/ui, React Query  
**Processing**: OpenRouter (LLM API gateway), PyMuPDF, pdfplumber, Crawl4AI, rapidfuzz  
**Infrastructure**: Docker, Flower (Celery monitoring), PostgreSQL 16, Redis 8, MinIO, Prometheus, Grafana, Loki

### Target Companies

- **Initial Scope**: 6 European companies seeded in database migrations
  - AstraZeneca PLC, SAP SE, Siemens AG, ASML Holding N.V., Unilever PLC, Allianz SE
- **Scalable**: Architecture supports adding more companies dynamically via API

## Documentation

📚 **[Full Documentation →](https://patrykquantumnomad.github.io/financial-data-extractor/)**

Complete documentation available on GitHub Pages including:

- Architecture overview and system design
- API reference with all endpoints
- Database schema and migrations
- Task processing with Celery
- Frontend development guide
- Infrastructure setup

## Quick Start

```bash
# Clone the repository
git clone https://github.com/PatrykQuantumNomad/financial-data-extractor.git
cd financial-data-extractor

# Setup infrastructure (PostgreSQL, Redis, MinIO, monitoring)
cd infrastructure
make up-dev

# Setup backend
cd ../backend
make install-dev
make migrate

# Start backend in one terminal
make run

# Start Celery worker in another terminal
make celery-worker

# Setup frontend in a third terminal
cd ../frontend
npm install
npm run dev
```

**Access Points:**
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:3030`
- API Docs: `http://localhost:3030/docs`
- Grafana: `http://localhost:3200` (admin/admin)
- Flower: `http://localhost:5555`
- MinIO Console: `http://localhost:9001`

For detailed setup instructions, see the [Full Documentation](https://patrykquantumnomad.github.io/financial-data-extractor/infrastructure-development).

## License

Apache 2.0 License. See [LICENSE](LICENSE) for details.
