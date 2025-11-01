# Financial Data Extractor - Backend

FastAPI backend for scraping, classifying, parsing, and compiling multi-year financial statements from European company investor relations websites.

## Tech Stack

- **FastAPI** - High-performance async web framework
- **Celery** - Distributed task queue
- **Flower** - Real-time Celery monitoring dashboard
- **PostgreSQL** - Primary database
- **Redis** - Caching and message broker
- **SQLAlchemy** - ORM
- **OpenAI GPT-5** - Financial statement extraction
- **PyMuPDF** - PDF processing

## Quick Start

### Prerequisites

- Python 3.13
- UV package manager
- PostgreSQL 16+
- Redis 7+

### Initial Setup

```bash
# Install all dependencies
make install-dev

# Run database migrations
make migrate

# Start development server
make run
```

## Development Workflows

All development tasks are managed through the Makefile. Run `make help` to see all available commands.

### Running the Application

```bash
# Start FastAPI development server (hot reload)
make run

# Start Celery worker for background tasks
make celery-worker

# Start Celery beat scheduler
make celery-beat

# Start Flower dashboard (task monitoring)
make celery-flower

# Test tasks via API
make test-task COMMAND="company-scrape 1"
```

See [Task Processing Documentation](../../docs/task-processing.md) for detailed information about the Celery task system.

### Testing

```bash
# Run all tests
make test

# Run unit tests only
make test-unit

# Run integration tests only
make test-integration

# Run tests with coverage report
make test-cov

# Watch mode for TDD
make test-watch
```

### Code Quality

```bash
# Run all code quality checks (lint + format + type + test)
make check

# Fix linting issues automatically
make lint-fix

# Format code with black
make format

# Run type checker
make type-check

# Quick check (fix linting and format)
make quick-check

# Pre-commit checks (lint + format + type + unit tests)
make pre-commit
```

### Database Migrations

```bash
# Run migrations
make migrate

# Upgrade to head revision
make migrate-up

# Rollback last migration
make migrate-down

# Create new migration
make migrate-create NAME="description"

# Show migration history
make migrate-history

# Database inspection (uses db_manager.py)
make db-list-companies  # List all companies with ticker details
make db-info            # Show database info and migration status
make db-reset           # Reset database (WARNING: destructive)
```

### Dependency Management

```bash
# Install all dependencies (including dev tools)
make install-dev

# Install production dependencies only
make install

# Add a new dependency
make add-dependency PKG="package-name"

# Add a dev dependency
make add-dev-dependency PKG="package-name"

# Update dependencies
make update-deps

# Update all dependencies
make update-deps-dev
```

### Task Testing

```bash
# Test a task (usage: make test-task COMMAND="company-scrape 1")
make test-task COMMAND="company-scrape 1"

# Test with auto-polling until completion
make test-task-poll COMMAND="company-scrape 1"

# Or use the script directly
./scripts/test_tasks.sh help
./scripts/test_tasks.sh company-scrape 1
```

See [Task Processing Documentation](../../docs/task-processing.md) for complete task management guide.

### Utilities

```bash
# Clean all caches and generated files
make clean

# Show project information
make info

# Show version information
make version

# Show all available commands
make help
```

## Development Best Practices

### Daily Workflow

```bash
# 1. Pull latest changes
git pull

# 2. Ensure dependencies are up to date
make install-dev

# 3. Run pre-commit checks before committing
make pre-commit

# 4. Start development server
make run
```

### Before Committing

```bash
# Run all checks to ensure code quality
make pre-commit

# Or manually run each check
make lint-fix      # Fix linting issues
make format        # Format code
make type-check    # Check types
make test-unit     # Run unit tests
```

### Adding Dependencies

```bash
# Add a production dependency
make add-dependency PKG="httpx"

# Add a development dependency
make add-dev-dependency PKG="pytest-mock"

# Check what was installed
make info
```

### Database Changes

```bash
# Create a new migration after model changes
make migrate-create NAME="add_user_table"

# Run migrations
make migrate

# Check migration history
make migrate-history
```

## Common Tasks

### Starting a Full Development Environment

```bash
# Terminal 1: Start FastAPI server
make run

# Terminal 2: Start Celery worker
make celery-worker

# Terminal 3: Start Celery beat (if needed)
make celery-beat
```

### Running Tests with Coverage

```bash
# Run all tests with coverage
make test-cov

# Coverage report will be generated at: htmlcov/index.html
open htmlcov/index.html
```

### Cleaning Up

```bash
# Clean all caches
make clean

# If issues persist, reinstall everything
make clean
rm -rf .venv uv.lock
make install-dev
```

## Troubleshooting

### Python Version Issues

```bash
# Check current Python version
make version

# If wrong version, UV will manage it automatically
make install-dev
```

### Dependency Issues

```bash
# Update all dependencies
make update-deps-dev

# Or clean and reinstall
make clean
rm -rf .venv uv.lock
make install-dev
```

### Database Issues

```bash
# Rollback last migration
make migrate-down

# Check migration status
make migrate-history
```

## License

Apache 2.0 - See [LICENSE](../LICENSE) for details.
