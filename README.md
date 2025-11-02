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
2. **Parse**: Extract financial data from Annual Reports using OpenAI GPT-5/LLM
3. **Compile**: Aggregate 10 years of financial data into unified views
4. **Deduplicate**: Align and merge similarly-named line items across years
5. **Prioritize Latest**: Use restated data from newer reports when available

### Technology Stack

**Backend**: FastAPI, Celery, PostgreSQL, Redis, SQLAlchemy, Alembic  
**Frontend**: Next.js 15, React 19, TypeScript, TailwindCSS, shadcn/ui  
**Processing**: OpenAI GPT-5, PyMuPDF, pdfplumber, Crawl4AI, rapidfuzz  
**Infrastructure**: Docker, Flower (Celery monitoring), PostgreSQL 16, Redis 8

### Target Companies

- **Initial Scope**: 2-3 European companies (e.g., Adyen, Heineken)
- **Scalable**: Architecture supports adding more companies dynamically

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

# Setup infrastructure (PostgreSQL, Redis, Flower)
cd infrastructure
make up

# Setup backend
cd ../backend
make install-dev
make migrate

# Start backend in one terminal
make run

# Start Celery worker in another terminal
cd backend
make celery-worker

# Setup frontend in a third terminal
cd frontend
npm install
npm run dev
```

For detailed setup instructions, see the [Full Documentation](https://patrykquantumnomad.github.io/financial-data-extractor/infrastructure-development).

## License

Apache 2.0 License. See [LICENSE](LICENSE) for details.
