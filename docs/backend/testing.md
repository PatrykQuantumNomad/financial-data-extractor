---
layout: default
title: Testing
description: Complete guide to pytest testing for FastAPI backend, unit tests, fixtures, and coverage
parent: Backend
nav_order: 3
---

# Backend Testing Guide

Complete guide to testing strategies, pytest configuration, and test implementation for the Financial Data Extractor FastAPI backend.

## Overview

The backend uses **pytest** as the primary testing framework with comprehensive test coverage for:

- API endpoints
- Middleware components
- Business logic
- Integration workflows
- Celery tasks

## Testing Principles

Our testing approach follows these core principles:

### 1. Test Behavior, Not Implementation

- Tests validate what the code does, not how it's implemented
- Focus on user-facing behavior and business requirements
- Tests remain stable during refactoring

### 2. Isolated Unit Tests

- Each unit test is independent and can run in any order
- External dependencies are mocked (databases, APIs, file systems)
- No side effects between tests
- Fast execution (< 1 second per test)

### 3. AAA Pattern (Arrange-Act-Assert)

All tests follow a consistent structure:

```python
def test_something():
    # Arrange - Set up test data and mocks
    mock_service.return_value = expected_data

    # Act - Execute the code under test
    result = function_under_test()

    # Assert - Verify the outcome
    assert result.status_code == 200
```

### 4. Comprehensive Coverage

- **Minimum 80% code coverage**, targeting 90%+
- Cover happy paths, error cases, and edge conditions
- Test boundary values and validation rules
- Include both positive and negative test cases

## Pytest Configuration

### Installation

Testing dependencies are included in the `dev` extras:

```bash
# Install with dev dependencies
cd backend
make install-dev

# Or with uv directly
uv sync --extra dev
```

### Configuration File

Pytest is configured in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "-ra",                    # Show extra test summary info
    "--strict-markers",       # Require markers to be registered
    "--cov=app",             # Measure coverage of app package
    "--cov-report=term-missing",  # Show missing lines in terminal
    "--cov-report=html",     # Generate HTML coverage report
]
asyncio_mode = "auto"        # Auto-detect async tests

[tool.coverage.run]
source = ["app"]
omit = [
    "*/tests/*",
    "*/test_*.py",
    "*/__pycache__/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
]
```

### Test Markers

Markers are used to categorize tests:

```python
@pytest.mark.unit          # Fast, isolated unit tests
@pytest.mark.integration   # Tests with real dependencies
@pytest.mark.slow          # Long-running tests (> 1 second)
```

## Running Tests

### Using Makefile Commands

```bash
# Run all tests
make test

# Run unit tests only
make test-unit

# Run integration tests only
make test-integration

# Run tests with coverage report
make test-cov

# Watch mode (auto-rerun on changes)
make test-watch
```

### Using pytest Directly

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/unit/api/test_companies_endpoints.py

# Run specific test class
uv run pytest tests/unit/api/test_companies_endpoints.py::TestCompaniesEndpoints

# Run specific test method
uv run pytest tests/unit/api/test_companies_endpoints.py::TestCompaniesEndpoints::test_create_company_success

# Run with verbose output
uv run pytest -v

# Run with coverage
uv run pytest --cov=app --cov-report=html

# Run tests matching a marker
uv run pytest -m unit

# Run tests excluding markers
uv run pytest -m "not slow"

# Run with parallel execution
uv run pytest -n auto
```

## Current Test Coverage

### Unit Tests

**Location:** `backend/tests/unit/`

**Status:** ✅ **124 unit tests** covering API endpoints, middleware, models, schemas, services, and utils

#### Test Files

| Category       | File                            | Tests | Coverage | Description               |
| -------------- | ------------------------------- | ----- | -------- | ------------------------- |
| **API**        | `test_companies_endpoints.py`   | 17    | 100%     | Company CRUD operations   |
| **API**        | `test_documents_endpoints.py`   | 17    | 100%     | Document management       |
| **API**        | `test_extractions_endpoints.py` | 15    | 100%     | Extraction operations     |
| **API**        | `test_error_handler.py`         | 13    | 100%     | Error handling middleware |
| **API**        | `test_middleware.py`            | 9     | 100%     | Request middleware        |
| **Models**     | `test_models.py`                | 12    | 100%     | DB models (Company, Document, Extraction) |
| **Schemas**    | `test_schemas.py`               | 18    | 100%     | Pydantic schemas validation |
| **Services**   | `test_company_service.py`       | 13    | 89%      | Business logic layer |
| **Utils**      | `test_file_utils.py`            | 7     | 81%      | File operations |
| **Utils**      | `test_log_filter.py`            | 4     | 100%     | Logging filters |

#### Coverage Highlights

**API Endpoints:**

- ✅ **Companies** - 100% coverage

  - Create, read, update, delete
  - List with pagination
  - Get by ticker
  - Input validation

- ✅ **Documents** - 100% coverage

  - CRUD operations
  - Filter by company, year, type
  - Pagination
  - Fiscal year validation

- ✅ **Extractions** - 100% coverage
  - CRUD operations
  - Filter by document and statement type
  - Complex data structures

**Middleware:**

- ✅ **ErrorHandler** - 100% coverage

  - All exception types
  - Problem Details (RFC 7807) format
  - Request ID inclusion
  - Proper HTTP status codes

- ✅ **RequestIDMiddleware** - 100% coverage

  - UUID generation
  - Header injection
  - Request isolation

- ✅ **TimeoutMiddleware** - 100% coverage
  - Timeout enforcement
  - 504 Gateway Timeout
  - Request cancellation

**Database Models:**

- ✅ **Company Model** - 100% coverage
  - Model instantiation
  - String representation
  - Nullable fields

- ✅ **Document Model** - 100% coverage
  - Model instantiation
  - String representation
  - Foreign key relationships

- ✅ **Extraction Models** - 100% coverage
  - Extraction and CompiledStatement models
  - Complex JSONB data structures

**Schemas:**

- ✅ **Company Schemas** - 100% coverage
  - CompanyBase, CompanyCreate, CompanyUpdate, CompanyResponse
  - Validation and field constraints

- ✅ **Document Schemas** - 100% coverage
  - DocumentBase, DocumentCreate, DocumentUpdate, DocumentResponse
  - Fiscal year validation

- ✅ **Extraction Schemas** - 100% coverage
  - ExtractionBase, ExtractionCreate, ExtractionUpdate, ExtractionResponse
  - CompiledStatement schemas

**Services:**

- ✅ **CompanyService** - 89% coverage
  - CRUD operations with error handling
  - HTTPException handling
  - Repository interaction

**Utils:**

- ✅ **file_utils** - 81% coverage
  - JSON file loading
  - Error handling (file not found, invalid JSON, encoding)
  - Complex data structures

- ✅ **log_filter** - 100% coverage
  - Log filtering logic
  - Suppression of specific entries
  - Case sensitivity

## Test Structure

### Directory Organization

```
backend/
├── tests/
│   ├── fixtures/                 # Shared test fixtures
│   │   ├── mock_responses/       # Mock HTTP responses
│   │   └── sample_pdfs/          # Sample PDF files
│   ├── integration/              # Integration tests (4 tests)
│   │   ├── __init__.py
│   │   ├── conftest.py           # Testcontainers setup
│   │   └── test_companies_integration.py
│   └── unit/                     # Unit tests (124 tests)
│       ├── api/                  # API unit tests (71 tests)
│       │   ├── __init__.py
│       │   ├── conftest.py       # Shared fixtures
│       │   ├── test_companies_endpoints.py
│       │   ├── test_documents_endpoints.py
│       │   ├── test_extractions_endpoints.py
│       │   ├── test_error_handler.py
│       │   └── test_middleware.py
│       ├── db/                   # DB model tests (12 tests)
│       │   ├── __init__.py
│       │   └── test_models.py
│       ├── schemas/              # Schema tests (15 tests)
│       │   ├── __init__.py
│       │   └── test_schemas.py
│       ├── services/             # Service tests (11 tests)
│       │   ├── __init__.py
│       │   ├── conftest.py       # Shared fixtures
│       │   └── test_company_service.py
│       └── utils/                # Utility tests (11 tests)
│           ├── __init__.py
│           ├── test_file_utils.py
│           └── test_log_filter.py
```

### Test Fixtures (`conftest.py`)

Shared fixtures are defined in `conftest.py`:

```python
# Mock services
@pytest.fixture
def mock_company_service() -> MagicMock:
    """Create a mock CompanyService for testing."""
    service = AsyncMock()
    service.create_company = AsyncMock()
    service.get_all_companies = AsyncMock()
    # ... more methods
    return service

# Sample data
@pytest.fixture
def sample_company_data() -> dict:
    """Sample company data for testing."""
    return {
        "id": 1,
        "name": "Test Company",
        "ir_url": "https://example.com/investor-relations",
        "primary_ticker": "TEST",
        "created_at": datetime(2024, 1, 1),
    }

# Test client
@pytest.fixture
def test_app(mock_company_service, ...) -> FastAPI:
    """Create a FastAPI test app with mocked dependencies."""
    app = FastAPI()
    app.include_router(companies_router)
    # Override dependencies with mocks
    app.dependency_overrides[...] = override_function
    return app

@pytest.fixture
def test_client(test_app: FastAPI) -> TestClient:
    """Create a TestClient for the test app."""
    return TestClient(test_app)
```

## Example Test Cases

### Testing Successful Endpoint

```python
@pytest.mark.unit
class TestCompaniesEndpoints:
    """Test cases for Companies endpoints."""

    def test_create_company_success(
        self,
        test_client: TestClient,
        mock_company_service,
        sample_company_data,
    ):
        """Test successful company creation."""
        # Arrange
        mock_company_service.create_company.return_value = sample_company_data
        company_data = {
            "name": "Test Company",
            "ir_url": "https://example.com/investor-relations",
            "primary_ticker": "TEST",
        }

        # Act
        response = test_client.post("/companies", json=company_data)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "Test Company"
        assert data["primary_ticker"] == "TEST"
        mock_company_service.create_company.assert_called_once()
```

### Testing Validation Errors

```python
def test_create_company_with_validation_error(
    self, test_client: TestClient, mock_company_service
):
    """Test company creation with invalid data."""
    # Arrange
    invalid_data = {"name": ""}  # Empty name should fail validation

    # Act
    response = test_client.post("/companies", json=invalid_data)

    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    mock_company_service.create_company.assert_not_called()
```

### Testing Middleware

```python
@pytest.mark.unit
class TestRequestIDMiddleware:
    """Test cases for RequestIDMiddleware."""

    @pytest.mark.asyncio
    async def test_generates_unique_request_id(
        self, middleware: RequestIDMiddleware, mock_request: MagicMock, mock_call_next: AsyncMock
    ):
        """Test that unique request ID is generated."""
        # Arrange - already set up

        # Act
        response = await middleware.dispatch(mock_request, mock_call_next)

        # Assert
        assert hasattr(mock_request.state, "request_id")
        assert isinstance(mock_request.state.request_id, str)

    @pytest.mark.asyncio
    async def test_request_id_added_to_response_header(
        self, middleware: RequestIDMiddleware, mock_request: MagicMock, mock_call_next: AsyncMock
    ):
        """Test that request ID is added to response header."""
        # Arrange - already set up

        # Act
        response = await middleware.dispatch(mock_request, mock_call_next)

        # Assert
        assert "X-Request-ID" in response.headers
        assert response.headers["X-Request-ID"] == mock_request.state.request_id
```

### Testing Error Handlers

```python
@pytest.mark.unit
class TestErrorHandler:
    """Test cases for ErrorHandler middleware."""

    @pytest.mark.asyncio
    async def test_forbidden_error_handler_returns_403(
        self, error_handler: ErrorHandler, mock_request: MagicMock
    ):
        """Test ForbiddenError handler returns 403."""
        # Arrange
        exc = ForbiddenError(detail="Access denied")
        expected_status = status.HTTP_403_FORBIDDEN

        # Act
        response = await error_handler.forbidden_error_handler(mock_request, exc)

        # Assert
        assert response.status_code == expected_status
        assert response.media_type == "application/problem+json"

        # Parse response body
        body = json.loads(response.body.decode())
        assert body["type"] == "https://httpstatuses.com/403"
        assert body["status"] == expected_status
        assert "Access denied" in body["detail"]
```

### Testing Services

```python
@pytest.mark.unit
class TestCompanyService:
    """Test cases for CompanyService."""

    @pytest.mark.asyncio
    async def test_create_company_success(
        self, mock_company_repository, sample_company_data
    ):
        """Test successful company creation."""
        # Arrange
        mock_company_repository.create.return_value = sample_company_data
        service = CompanyService(mock_company_repository)
        company_data = CompanyCreate(
            name="Test Company",
            ir_url="https://example.com/ir",
            primary_ticker="TEST",
        )

        # Act
        result = await service.create_company(company_data)

        # Assert
        assert result == sample_company_data
        mock_company_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_company_not_found(self, mock_company_repository):
        """Test company retrieval when not found raises HTTPException."""
        # Arrange
        mock_company_repository.get_by_id.return_value = None
        service = CompanyService(mock_company_repository)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await service.get_company(999)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "Company with id 999 not found" in exc_info.value.detail
```

### Testing File Utils

```python
@pytest.mark.unit
class TestFileUtils:
    """Test cases for file utility functions."""

    def test_load_json_file_success(self):
        """Test successful JSON file loading."""
        # Arrange
        test_data = {"name": "Test Company", "ticker": "TEST"}
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump(test_data, f)
            temp_file = f.name

        try:
            # Act
            result = load_json_file(temp_file)

            # Assert
            assert result == test_data
        finally:
            # Cleanup
            Path(temp_file).unlink()

    def test_load_json_file_not_found(self):
        """Test loading non-existent JSON file raises FileNotFoundError."""
        # Arrange
        non_existent_file = "/path/to/non/existent/file.json"

        # Act & Assert
        with pytest.raises(JSONFileNotFoundError):
            load_json_file(non_existent_file)
```

## Best Practices

### Naming Conventions

- **Test files**: `test_*.py` or `*_test.py`
- **Test classes**: `TestClassName`
- **Test methods**: `test_should_describe_what_is_being_tested`
- Use descriptive names that explain what is being tested

✅ **Good**: `test_create_company_with_invalid_name_returns_422`  
❌ **Bad**: `test1`, `test_create`

### Test Isolation

- Each test should be independent
- Clean up resources in fixtures using `yield` or `finalizer`
- Use `monkeypatch` for environment variables
- Mock external dependencies

```python
@pytest.fixture
def temp_file(tmp_path):
    """Create temporary file that is cleaned up after test."""
    file_path = tmp_path / "test_file.txt"
    file_path.write_text("test content")
    yield file_path
    file_path.unlink()  # Cleanup
```

### Mocking External Services

Always mock external dependencies in unit tests:

```python
@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client."""
    with patch('app.core.llm.client') as mock:
        mock.chat.completions.create.return_value = {
            "choices": [{"message": {"content": "mocked response"}}]
        }
        yield mock
```

### Testing Async Code

Use `pytest.mark.asyncio` for async tests:

```python
@pytest.mark.asyncio
async def test_async_operation():
    result = await some_async_function()
    assert result is not None
```

### Coverage Goals

- **Minimum**: 80% overall coverage
- **Target**: 90%+ overall coverage
- **Critical paths**: 100% coverage
- Use coverage reports to identify gaps

## Running Tests in CI/CD

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: "3.13"
      - name: Install dependencies
        run: |
          pip install uv
          uv sync --extra dev
      - name: Run linting
        run: make lint
      - name: Run unit tests
        run: make test-unit
      - name: Generate coverage report
        run: make test-cov
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
```

## Integration Testing

Integration tests use **testcontainers** to spin up real PostgreSQL database instances and test complete workflows from API to database. This ensures that the entire request flow (API → Service → Repository → Database) works correctly with real database connections and Alembic migrations.

**Location:** `backend/tests/integration/`

**Status:** ✅ **4 integration tests** covering Companies API CRUD workflows with real PostgreSQL database

### Testcontainers

Integration tests use [testcontainers-python](https://testcontainers-python.readthedocs.io/en/latest/) to automatically manage Docker containers for dependencies:

- **PostgreSQL**: Real PostgreSQL 16 database instance for testing
- **Alembic Migrations**: Full schema initialization with migrations
- **Connection Pool**: Real async connection pool testing
- **Future**: Redis, Celery workers, external services

**Key Features:**

1. **Automatic Container Management**: Containers start and stop automatically
2. **Isolated Test Sessions**: Fresh database for each test session
3. **Real Database**: Tests against actual PostgreSQL, not mocks
4. **Migration Testing**: Validates Alembic migrations work correctly
5. **CI/CD Ready**: Works in Docker and GitHub Actions environments

```python
from testcontainers.postgres import PostgresContainer

@pytest.fixture(scope="session")
def postgres_container():
    """Create a PostgreSQL testcontainer for integration tests."""
    with PostgresContainer("postgres:16", driver="psycopg3") as postgres:
        yield postgres
```

### Setup and Fixtures

The integration test setup includes:

```python
@pytest.fixture(scope="session")
def postgres_container():
    """PostgreSQL container started once per test session."""
    with PostgresContainer("postgres:16", driver="psycopg3") as postgres:
        yield postgres

@pytest.fixture(scope="session", autouse=True)
def database_initialized(postgres_container, alembic_cfg):
    """Run Alembic migrations to initialize database schema."""
    command.upgrade(alembic_cfg, "head")

@pytest.fixture
def test_app(database_initialized, db_url):
    """Create FastAPI app with real database."""
    # Set environment variables for testcontainer
    # Create app
    app = create_app()
    yield app

@pytest.fixture
def test_client(test_app):
    """TestClient with proper lifespan handling."""
    with TestClient(test_app) as client:
        yield client
```

### Integration Test Examples

**Complete CRUD Workflow:**

```python
@pytest.mark.integration
class TestCompaniesIntegration:
    """Integration tests for Companies CRUD workflow."""

    def test_create_read_update_delete_company_workflow(self, test_client):
        """Test complete CRUD workflow for a company."""
        # Create
        create_response = test_client.post(
            "/api/v1/companies",
            json={"name": "Test", "ir_url": "https://example.com", "primary_ticker": "TCI"}
        )
        assert create_response.status_code == 201
        company_id = create_response.json()["id"]

        # Read
        get_response = test_client.get(f"/api/v1/companies/{company_id}")
        assert get_response.status_code == 200
        
        # Update
        update_response = test_client.put(
            f"/api/v1/companies/{company_id}",
            json={"name": "Updated"}
        )
        assert update_response.status_code == 200
        
        # Delete
        delete_response = test_client.delete(f"/api/v1/companies/{company_id}")
        assert delete_response.status_code == 204
```

**Current Coverage:**

| Test | Description | Status |
|------|-------------|--------|
| `test_create_read_update_delete_company_workflow` | Complete CRUD lifecycle | ✅ |
| `test_list_companies_with_pagination` | List with pagination | ✅ |
| `test_get_company_by_ticker` | Get by ticker symbol | ✅ |
| `test_create_multiple_companies_success` | Multiple companies | ✅ |

### Running Integration Tests

```bash
# Run all integration tests
make test-integration

# Or with pytest directly
uv run pytest -m integration

# Run specific test
uv run pytest tests/integration/test_companies_integration.py -v

# Run with coverage
uv run pytest -m integration --cov=app
```

### Benefits of Integration Tests

1. **Real Database**: Tests against actual PostgreSQL, catching SQL/transaction issues
2. **Full Stack**: Validates API → Service → Repository → Database flow
3. **Alembic Migrations**: Tests schema with actual migrations
4. **Isolation**: Each test session gets a fresh database
5. **CI/CD Ready**: Works in Docker and GitHub Actions

### Future Integration Tests

- Document CRUD workflows
- Extraction CRUD workflows
- CompiledStatement operations
- Celery task execution with Redis
- Multi-step workflows (scrape → extract → compile)

## Troubleshooting

### Tests Failing Intermittently

**Possible causes:**

- Shared state between tests
- Timing issues in async code
- Unmocked external calls

**Solutions:**

- Ensure proper test isolation
- Use proper async test setup
- Mock all external dependencies

### Slow Test Execution

**Optimizations:**

- Run tests in parallel: `pytest -n auto`
- Use markers to skip slow tests: `pytest -m "not slow"`
- Optimize fixtures to avoid unnecessary work
- Consider test database vs. production database

### Coverage Gaps

Use coverage reports to identify:

```bash
# Generate HTML report
make test-cov

# Open in browser
open backend/htmlcov/index.html
```

### Debugging Failed Tests

```bash
# Run with verbose output and no capture
uv run pytest -vvs tests/unit/api/test_companies_endpoints.py::test_create_company_success

# Run with debugging
uv run pytest --pdb tests/unit/api/test_companies_endpoints.py::test_create_company_success

# Show local variables on failure
uv run pytest -l tests/unit/api/test_companies_endpoints.py::test_create_company_success
```

## Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio Documentation](https://pytest-asyncio.readthedocs.io/)
- [pytest-mock Documentation](https://pytest-mock.readthedocs.io/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [FastAPI Testing Documentation](https://fastapi.tiangolo.com/tutorial/testing/)

## Next Steps

1. ✅ **Unit tests** - API endpoints, middleware, models, schemas, services, utils (124 tests)
2. 🔄 **Integration tests** - Database and external services (in progress)
3. ⏳ **Additional service tests** - Document, Extraction, CompiledStatement services
4. ⏳ **Repository tests** - Database layer with mocked connections
5. ⏳ **End-to-end tests** - Complete workflows
6. ⏳ **Performance tests** - Load and stress testing
7. ⏳ **Security tests** - Vulnerability scanning
