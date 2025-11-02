---
layout: default
title: Backend Testing
description: Complete guide to pytest testing for FastAPI backend, unit tests, fixtures, and coverage
nav_order: 8
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

**Location:** `backend/tests/unit/api/`

**Status:** ✅ **70 unit tests** covering API endpoints and middleware

#### Test Files

| File                            | Tests | Coverage | Description               |
| ------------------------------- | ----- | -------- | ------------------------- |
| `test_companies_endpoints.py`   | 17    | 100%     | Company CRUD operations   |
| `test_documents_endpoints.py`   | 17    | 100%     | Document management       |
| `test_extractions_endpoints.py` | 15    | 100%     | Extraction operations     |
| `test_error_handler.py`         | 13    | 100%     | Error handling middleware |
| `test_middleware.py`            | 9     | 100%     | Request middleware        |

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

## Test Structure

### Directory Organization

```
backend/
├── tests/
│   ├── fixtures/                 # Shared test fixtures
│   │   ├── mock_responses/       # Mock HTTP responses
│   │   └── sample_pdfs/          # Sample PDF files
│   ├── integration/              # Integration tests
│   │   └── ...                   # (Coming soon)
│   └── unit/                     # Unit tests
│       └── api/                  # API unit tests
│           ├── __init__.py
│           ├── conftest.py       # Shared fixtures
│           ├── test_companies_endpoints.py
│           ├── test_documents_endpoints.py
│           ├── test_extractions_endpoints.py
│           ├── test_error_handler.py
│           └── test_middleware.py
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

## Integration Testing (Coming Soon)

Integration tests will cover:

- Full request-response cycles
- Database interactions with real PostgreSQL
- Celery task execution
- Redis integration
- External API interactions

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

1. ✅ **Unit tests** - API endpoints and middleware (70 tests)
2. 🔄 **Integration tests** - Database and external services (in progress)
3. ⏳ **End-to-end tests** - Complete workflows
4. ⏳ **Performance tests** - Load and stress testing
5. ⏳ **Security tests** - Vulnerability scanning
