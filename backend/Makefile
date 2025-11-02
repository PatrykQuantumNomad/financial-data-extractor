.PHONY: help install install-dev clean test test-unit test-integration test-cov lint lint-fix format type-check check run dev migrate migrate-up migrate-down migrate-create shell update-deps update-deps-dev crawl4ai-setup crawl4ai-doctor

# Variables
PYTHON := uv run python
UV := uv
VENV := .venv
APP := app
TESTS := tests

# Colors for output
COLOR_RESET := \033[0m
COLOR_BOLD := \033[1m
COLOR_GREEN := \033[32m
COLOR_YELLOW := \033[33m
COLOR_BLUE := \033[34m
COLOR_CYAN := \033[36m

.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "$(COLOR_BOLD)Financial Data Extractor - Backend$(COLOR_RESET)"
	@echo ""
	@echo "$(COLOR_BOLD)Available commands:$(COLOR_RESET)"
	@echo ""
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(COLOR_CYAN)%-20s$(COLOR_RESET) %s\n", $$1, $$2}'
	@echo ""

# Installation
install: ## Install production dependencies
	@echo "$(COLOR_GREEN)Installing production dependencies...$(COLOR_RESET)"
	$(UV) sync --no-dev
	@echo "$(COLOR_GREEN)Running Crawl4AI post-installation setup...$(COLOR_RESET)"
	$(UV) run crawl4ai-setup || echo "$(COLOR_YELLOW)Crawl4AI setup had warnings (this may be normal)$(COLOR_RESET)"
	@echo "$(COLOR_GREEN)✓ Installation complete!$(COLOR_RESET)"

install-dev: ## Install all dependencies including dev tools
	@echo "$(COLOR_GREEN)Installing all dependencies (including dev)...$(COLOR_RESET)"
	$(UV) sync --extra dev
	@echo "$(COLOR_GREEN)Running Crawl4AI post-installation setup...$(COLOR_RESET)"
	$(UV) run crawl4ai-setup || echo "$(COLOR_YELLOW)Crawl4AI setup had warnings (this may be normal)$(COLOR_RESET)"
	@echo "$(COLOR_GREEN)✓ Development environment ready!$(COLOR_RESET)"

crawl4ai-setup: ## Run Crawl4AI post-installation setup
	@echo "$(COLOR_GREEN)Running Crawl4AI setup...$(COLOR_RESET)"
	$(UV) run crawl4ai-setup
	@echo "$(COLOR_GREEN)✓ Crawl4AI setup complete!$(COLOR_RESET)"

crawl4ai-doctor: ## Verify Crawl4AI installation
	@echo "$(COLOR_GREEN)Verifying Crawl4AI installation...$(COLOR_RESET)"
	$(UV) run crawl4ai-doctor
	@echo "$(COLOR_GREEN)✓ Crawl4AI verification complete!$(COLOR_RESET)"

clean: ## Clean generated files and caches
	@echo "$(COLOR_YELLOW)Cleaning up...$(COLOR_RESET)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	@echo "$(COLOR_GREEN)✓ Clean complete!$(COLOR_RESET)"

# Testing
test: ## Run all tests
	@echo "$(COLOR_GREEN)Running all tests...$(COLOR_RESET)"
	$(UV) run pytest

test-unit: ## Run unit tests only
	@echo "$(COLOR_GREEN)Running unit tests...$(COLOR_RESET)"
	$(UV) run pytest -m unit

test-integration: ## Run integration tests only
	@echo "$(COLOR_GREEN)Running integration tests...$(COLOR_RESET)"
	$(UV) run pytest -m integration

test-cov: ## Run tests with coverage report
	@echo "$(COLOR_GREEN)Running tests with coverage...$(COLOR_RESET)"
	$(UV) run pytest --cov=$(APP) --cov-report=term-missing --cov-report=html
	@echo "$(COLOR_CYAN)Coverage report generated: htmlcov/index.html$(COLOR_RESET)"

test-watch: ## Run tests in watch mode
	@echo "$(COLOR_GREEN)Running tests in watch mode...$(COLOR_RESET)"
	$(UV) run pytest-watch

# Linting & Formatting
lint: ## Run all linters (ruff, mypy)
	@echo "$(COLOR_GREEN)Running linters...$(COLOR_RESET)"
	@echo "$(COLOR_BLUE)Checking with ruff...$(COLOR_RESET)"
	@$(UV) run ruff check $(APP) $(TESTS) || true
	@echo "$(COLOR_BLUE)Checking types with mypy...$(COLOR_RESET)"
	@$(UV) run mypy $(APP) || true
	@echo "$(COLOR_GREEN)✓ Linting complete!$(COLOR_RESET)"

lint-fix: ## Auto-fix linting issues
	@echo "$(COLOR_GREEN)Fixing linting issues...$(COLOR_RESET)"
	@$(UV) run ruff check --fix $(APP) $(TESTS) || true
	@echo "$(COLOR_GREEN)✓ Auto-fix complete!$(COLOR_RESET)"

format: ## Format code with black
	@echo "$(COLOR_GREEN)Formatting code...$(COLOR_RESET)"
	$(UV) run black $(APP) $(TESTS)
	@echo "$(COLOR_GREEN)✓ Formatting complete!$(COLOR_RESET)"

type-check: ## Run type checker (mypy)
	@echo "$(COLOR_GREEN)Running type checker...$(COLOR_RESET)"
	$(UV) run mypy $(APP)
	@echo "$(COLOR_GREEN)✓ Type checking complete!$(COLOR_RESET)"

# Quality checks
check: lint format type-check test ## Run all checks (lint, format, type-check, test)
	@echo "$(COLOR_GREEN)✓ All checks passed!$(COLOR_RESET)"

# Running the application
run: ## Run the FastAPI server via run.py
	@echo "$(COLOR_GREEN)Starting FastAPI server (run.py)...$(COLOR_RESET)"
	$(UV) run python run.py

# Celery
celery-worker: ## Start Celery worker (listens to all queues)
	@echo "$(COLOR_GREEN)Starting Celery worker...$(COLOR_RESET)"
	@echo "$(COLOR_YELLOW)Listening to queues: scraping, extraction, compilation, orchestration, default$(COLOR_RESET)"
	$(UV) run celery -A app.tasks.celery_app worker --loglevel=info -Q scraping,extraction,compilation,orchestration,default

celery-beat: ## Start Celery beat scheduler
	@echo "$(COLOR_GREEN)Starting Celery beat scheduler...$(COLOR_RESET)"
	$(UV) run celery -A app.tasks.celery_app beat --loglevel=info

celery-flower: ## Start Flower dashboard for Celery monitoring
	@echo "$(COLOR_GREEN)Starting Flower dashboard...$(COLOR_RESET)"
	@echo "$(COLOR_YELLOW)Flower will be available at http://localhost:5555$(COLOR_RESET)"
	@echo "$(COLOR_YELLOW)Persistent mode enabled to show task history$(COLOR_RESET)"
	$(UV) run celery -A app.tasks.celery_app flower --port=5555 --persistent=True

# Database migrations
migrate: migrate-up ## Alias for migrate-up

migrate-up: ## Run database migrations
	@echo "$(COLOR_GREEN)Running database migrations...$(COLOR_RESET)"
	$(UV) run alembic upgrade head
	@echo "$(COLOR_GREEN)✓ Migrations complete!$(COLOR_RESET)"

migrate-down: ## Rollback last migration
	@echo "$(COLOR_YELLOW)Rolling back last migration...$(COLOR_RESET)"
	$(UV) run alembic downgrade -1
	@echo "$(COLOR_GREEN)✓ Rollback complete!$(COLOR_RESET)"

migrate-create: ## Create a new migration (usage: make migrate-create NAME="migration_name")
	@echo "$(COLOR_GREEN)Creating new migration...$(COLOR_RESET)"
	$(UV) run alembic revision --autogenerate -m "$(NAME)"
	@echo "$(COLOR_GREEN)✓ Migration created!$(COLOR_RESET)"

migrate-history: ## Show migration history
	@echo "$(COLOR_GREEN)Migration history:$(COLOR_RESET)"
	$(UV) run alembic history

# Utilities
add-dependency: ## Add a new dependency (usage: make add-dependency PKG="package_name")
	@echo "$(COLOR_GREEN)Adding dependency: $(PKG)...$(COLOR_RESET)"
	$(UV) add $(PKG)
	@echo "$(COLOR_GREEN)✓ Dependency added!$(COLOR_RESET)"

add-dev-dependency: ## Add a new dev dependency (usage: make add-dev-dependency PKG="package_name")
	@echo "$(COLOR_GREEN)Adding dev dependency: $(PKG)...$(COLOR_RESET)"
	$(UV) add --dev $(PKG)
	@echo "$(COLOR_GREEN)✓ Dev dependency added!$(COLOR_RESET)"

update-deps: ## Update all dependencies
	@echo "$(COLOR_YELLOW)Updating dependencies...$(COLOR_RESET)"
	$(UV) sync --upgrade
	@echo "$(COLOR_GREEN)✓ Dependencies updated!$(COLOR_RESET)"

update-deps-dev: ## Update all dependencies including dev extras
	@echo "$(COLOR_YELLOW)Updating dependencies (including dev extras)...$(COLOR_RESET)"
	$(UV) sync --upgrade --extra dev
	@echo "$(COLOR_GREEN)✓ Dev dependencies updated!$(COLOR_RESET)"

# Development workflow helpers
quick-check: lint-fix format ## Quick check: fix linting and format code
	@echo "$(COLOR_GREEN)✓ Quick check complete!$(COLOR_RESET)"

pre-commit: lint-fix format ## Run pre-commit checks (fix linting and format code)
	@echo "$(COLOR_GREEN)✓ Pre-commit checks passed!$(COLOR_RESET)"

ci: lint type-check test ## Run CI checks (no fixes)
	@echo "$(COLOR_GREEN)✓ CI checks passed!$(COLOR_RESET)"

# Docker helpers (for future use)
docker-build: ## Build Docker image
	@echo "$(COLOR_GREEN)Building Docker image...$(COLOR_RESET)"
	docker build -t financial-data-extractor:latest .

docker-run: ## Run Docker container
	@echo "$(COLOR_GREEN)Running Docker container...$(COLOR_RESET)"
	docker run -p 8000:8000 financial-data-extractor:latest

# Database helpers
db-reset: ## Reset database (WARNING: destructive)
	@echo "$(COLOR_YELLOW)⚠️  WARNING: This will destroy all data!$(COLOR_RESET)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		$(UV) run alembic downgrade base; \
		$(UV) run alembic upgrade head; \
		echo "$(COLOR_GREEN)✓ Database reset!$(COLOR_RESET)"; \
	fi

db-list-companies: ## List all companies in database
	@echo "$(COLOR_GREEN)Listing companies...$(COLOR_RESET)"
	@$(UV) run python scripts/db_manager.py list-companies

db-info: ## Show database info and migration status
	@echo "$(COLOR_GREEN)Database information:$(COLOR_RESET)"
	@$(UV) run python scripts/db_manager.py info

db-shell: ## Open database shell
	@echo "$(COLOR_GREEN)Opening database shell...$(COLOR_RESET)"
	# TODO: Add database connection command when .env is configured
	@echo "$(COLOR_YELLOW)⚠️  Configure database connection in .env$(COLOR_RESET)"

# Monitoring & Debugging
logs: ## Tail application logs
	@echo "$(COLOR_GREEN)Tailing logs...$(COLOR_RESET)"
	tail -f logs/app.log 2>/dev/null || echo "$(COLOR_YELLOW)No log file found$(COLOR_RESET)"

psql: ## Connect to PostgreSQL (requires .env configuration)
	@echo "$(COLOR_GREEN)Connecting to PostgreSQL...$(COLOR_RESET)"
	# TODO: Add psql command when .env is configured
	@echo "$(COLOR_YELLOW)⚠️  Configure database in .env$(COLOR_RESET)"

redis-cli: ## Connect to Redis CLI
	@echo "$(COLOR_GREEN)Connecting to Redis...$(COLOR_RESET)"
	redis-cli

# Project info
info: ## Show project information
	@echo "$(COLOR_BOLD)Project Information:$(COLOR_RESET)"
	@echo "  Name: Financial Data Extractor Backend"
	@echo "  Version: $$(grep '^version' pyproject.toml | cut -d '"' -f 2)"
	@echo "  Python: $$($(PYTHON) --version)"
	@echo "  UV: $$($(UV) --version)"
	@echo ""
	@echo "$(COLOR_BOLD)Installed packages:$(COLOR_RESET)"
	@$(UV) pip list | tail -n +2 | wc -l | awk '{print "  Total:", $$1, "packages"}'

version: ## Show version information
	@echo "Version: $$(grep '^version' pyproject.toml | cut -d '"' -f 2)"
	@echo "Python: $$($(PYTHON) --version)"
	@echo "UV: $$($(UV) --version)"

# Task testing
test-task: ## Test Celery tasks (usage: make test-task COMMAND="company-scrape 1")
	@if [ -z "$(COMMAND)" ]; then \
		echo "$(COLOR_YELLOW)Usage: make test-task COMMAND=\"company-scrape 1\"$(COLOR_RESET)"; \
		echo "$(COLOR_CYAN)Run: ./scripts/test_tasks.sh help$(COLOR_RESET)"; \
	else \
		./scripts/test_tasks.sh $(COMMAND); \
	fi

test-task-poll: ## Test Celery task with polling (usage: make test-task-poll COMMAND="company-scrape 1")
	@if [ -z "$(COMMAND)" ]; then \
		echo "$(COLOR_YELLOW)Usage: make test-task-poll COMMAND=\"company-scrape 1\"$(COLOR_RESET)"; \
		echo "$(COLOR_CYAN)Run: ./scripts/test_tasks.sh help$(COLOR_RESET)"; \
	else \
		POLL=true ./scripts/test_tasks.sh $(COMMAND); \
	fi
